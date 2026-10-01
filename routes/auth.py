from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    status,
)

from fastapi.responses import (
    JSONResponse,
    RedirectResponse,
)

from ..auth import (
    clear_auth_cookie,
    create_access_token,
    get_current_user,
    hash_password,
    set_auth_cookie,
    verify_password,
)

from ..database import (
    create_user,
    get_user_by_email,
    list_recommendations,
)

from ..models import (
    LoginRequest,
    RegisterRequest,
)


router = APIRouter()


def user_public(row):

    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
    }


@router.post("/register")
async def register(
    payload: RegisterRequest,
):

    if get_user_by_email(
        payload.email
    ):

        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )

    user = create_user(
        payload.email,
        payload.name,
        hash_password(
            payload.password
        ),
    )

    token = create_access_token(
        user["id"]
    )

    response = JSONResponse(
        {
            "message": (
                "Registration successful"
            ),
            "user": user,
        }
    )

    set_auth_cookie(
        response,
        token,
    )

    return response


@router.post("/login")
async def login(
    payload: LoginRequest,
):

    user = get_user_by_email(
        payload.email
    )

    if (
        not user
        or not verify_password(
            payload.password,
            user["password_hash"],
        )
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(
        user["id"]
    )

    response = JSONResponse(
        {
            "message": "Login successful",
            "user": user_public(user),
        }
    )

    set_auth_cookie(
        response,
        token,
    )

    return response


@router.post("/token")
async def token(
    payload: LoginRequest,
):

    user = get_user_by_email(
        payload.email
    )

    if (
        not user
        or not verify_password(
            payload.password,
            user["password_hash"],
        )
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    jwt_token = create_access_token(
        user["id"]
    )

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": user_public(user),
    }


@router.post("/logout")
async def logout():

    response = RedirectResponse(
        "/login",
        status_code=303,
    )

    clear_auth_cookie(
        response
    )

    return response


@router.get("/session-info")
async def session_info(
    request: Request,
):

    user = get_current_user(
        request
    )

    return {
        "logged_in": True,
        "user_id": user["id"],
        "email": user["email"],
        "name": user["name"],
    }


@router.get("/session-data")
async def session_data(
    request: Request,
):

    user = get_current_user(
        request
    )

    history = list_recommendations(
        user["id"],
        10,
    )

    return {
        "user": user_public(user),
        "recommendation_count": len(
            history
        ),
        "recent": history,
    }