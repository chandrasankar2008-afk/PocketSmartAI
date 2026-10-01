from typing import Any, Literal

from pydantic import (
    BaseModel,
    Field,
)


class RegisterRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=80,
    )

    email: str = Field(
        min_length=5,
        max_length=160,
    )

    password: str = Field(
        min_length=6,
        max_length=128,
    )


class LoginRequest(BaseModel):
    email: str = Field(
        min_length=5,
        max_length=160,
    )

    password: str = Field(
        min_length=1,
        max_length=128,
    )


class HomeRequest(BaseModel):
    total_budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    rooms: list[str] = Field(
        min_length=1,
        max_length=10,
    )

    lights: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    ceiling_fans: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    dining_tables: int = Field(
        default=0,
        ge=0,
        le=20,
    )

    furniture: int = Field(
        default=0,
        ge=0,
        le=100,
    )

    style: str = Field(
        default="modern",
        max_length=80,
    )

    additional_requirements: str = Field(
        default="",
        max_length=1000,
    )


class PartyRequest(BaseModel):
    total_budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    guests: int = Field(
        gt=0,
        le=10_000,
    )

    event_type: str = Field(
        min_length=2,
        max_length=80,
    )

    venue: str = Field(
        default="not specified",
        max_length=160,
    )

    catering: bool = True

    decoration: bool = True

    entertainment: bool = True

    accommodation: bool = False

    additional_requirements: str = Field(
        default="",
        max_length=1000,
    )


class JewelryRequest(BaseModel):
    total_budget: float = Field(
        gt=0,
        le=10_000_000,
    )

    occasion: str = Field(
        min_length=2,
        max_length=100,
    )

    style: str = Field(
        default="elegant",
        max_length=100,
    )

    preferences: str = Field(
        default="",
        max_length=1000,
    )


class RecommendationResponse(BaseModel):
    total_budget: float

    budget_breakdown: list[
        dict[str, Any]
    ] = []

    recommendations: list[
        dict[str, Any]
    ] = []

    remaining_budget: float

    tips: list[str] = []

    source: Literal[
        "gemini",
        "fallback",
    ]

    recommendation_id: int | None = None