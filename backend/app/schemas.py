from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import ApplicationStatus


class TokenPair(BaseModel):
    access_token: str = Field(examples=["eyJhbGciOiJI..."])
    refresh_token: str = Field(examples=["eyJhbGciOiJI..."])
    token_type: str = Field(default="bearer")


class LoginRequest(BaseModel):
    email: EmailStr = Field(examples=["user@example.com"])
    password: str = Field(examples=["StrongPass!123"])


class RefreshRequest(BaseModel):
    refresh_token: str = Field(examples=["eyJhbGciOiJI..."])


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = Field(default=None, examples=["eyJhbGciOiJI..."])
    logout_all: bool = Field(default=False, examples=[False])


class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(examples=["user@example.com"])


class PasswordResetConfirm(BaseModel):
    token: str = Field(examples=["reset-token"])
    new_password: str = Field(examples=["NewStrongPass!123"])


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: Optional[str] = None
    locale: str
    time_zone: str
    created_at: datetime
    updated_at: datetime


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    company: str
    status: ApplicationStatus
    source: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AuditEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    event_type: str
    details: Dict[str, Any]
    created_at: datetime
