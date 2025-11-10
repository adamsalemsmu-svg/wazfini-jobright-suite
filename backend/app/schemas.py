from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

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
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    resume_skills: Optional[list[str]] = None
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


class JobState(str, Enum):
    recommended = "recommended"
    saved = "saved"
    applied = "applied"


class JobOut(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str] = None
    salary_low: Optional[float] = None
    salary_high: Optional[float] = None
    currency: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    industry: Optional[str] = None
    education_level: Optional[str] = None
    work_mode: Optional[str] = None
    posted_date: Optional[datetime] = None
    apply_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    source: Optional[str] = None
    state: JobState = JobState.recommended


class JobFilters(BaseModel):
    location: Optional[str] = None
    industry: Optional[str] = None
    experience_level: Optional[str] = None
    job_type: Optional[str] = None
    education_level: Optional[str] = None
    work_mode: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    posted_within_days: Optional[int] = Field(default=None, ge=0)
    q: Optional[str] = None


class AutomationProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None
    cover_letter: Optional[str] = None


class ResumePayload(BaseModel):
    filename: str = Field(default="resume.pdf", max_length=255)
    content_b64: str


class JobAutomationRequest(BaseModel):
    platform: str = Field(pattern="^(greenhouse|workday|bayt)$")
    job_url: HttpUrl
    profile: AutomationProfile
    resume: Optional[ResumePayload] = None
    notify_email: Optional[EmailStr] = None
    notify_phone: Optional[str] = Field(default=None, max_length=32)


class JobAutomationResponse(BaseModel):
    task_id: str
    status: str = Field(default="queued")
