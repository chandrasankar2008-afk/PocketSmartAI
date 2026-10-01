import hashlib
import hmac
import os

from datetime import (
    datetime,
    timedelta,
    timezone,
)

import jwt

from fastapi import (
    HTTPException,
    Request,
    status,
)

from .config import SECRET_KEY
from .database import get_user_by_id


ALGORITHM = "HS256"

TOKEN_EXPIRE_MINUTES = 120

COOKIE_NAME = "pocketsmart_access_token"


def hash_password(
    password: str,
) -> str:

    salt = os.urandom(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        120_000,
    )

    return (
        "pbkdf2_sha256$120000$"
        f"{salt.hex()}$"
        f"{digest.hex()}"
    )


def verify_password(
    password: str,
    encoded: str,
) -> bool:

    try:

        (
            _,
            iterations,
            salt_hex,
            digest_hex,
        ) = encoded.split(
            "$",
            3,
        )

        salt = bytes.fromhex(
            salt_hex
        )

        expected = bytes.fromhex(
            digest_hex
        )

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt,
            int(iterations),
        )

        return hmac.compare_digest(
            actual,
            expected,
        )

    except (
        ValueError,
        TypeError,
    ):
        return False


def create_access_token(
    user_id: int,
) -> str:

    now = datetime.now(
        timezone.utc
    )

    expires = now + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires,
        "iat": now,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_token_from_request(
    request: Request,
) -> str | None:

    authorization = request.headers.get(
        "Authorization",
        "",
    )

    if authorization.lower().startswith(
        "bearer "
    ):
        return authorization[7:].strip()

    return request.cookies.get(
        COOKIE_NAME
    )


def get_current_user(
    request: Request,
):

    token = get_token_from_request(
        request
    )

    if not token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = int(
            payload["sub"]
        )

    except (
        jwt.PyJWTError,
        KeyError,
        ValueError,
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = get_user_by_id(
        user_id
    )

    if not user:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def set_auth_cookie(
    response,
    token: str,
) -> None:

    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=TOKEN_EXPIRE_MINUTES * 60,
    )


def clear_auth_cookie(
    response,
) -> None:

    response.delete_cookie(
        COOKIE_NAME
    )