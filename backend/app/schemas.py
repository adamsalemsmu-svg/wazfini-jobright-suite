from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class ExperienceIn(BaseModel):
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class EducationIn(BaseModel):
    school: str
    degree: Optional[str] = None
    gpa: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ProfileIn(BaseModel):
    user_email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = None
    experiences: List[ExperienceIn] = []
    educations: List[EducationIn] = []
    skills: List[str] = []

class JobOut(BaseModel):
    id: int
    title: str
    company: str
    location: str
    salary_low: Optional[int]
    salary_high: Optional[int]
    currency: str
    job_type: Optional[str]
    experience_level: Optional[str]
    industry: Optional[str]
    education_level: Optional[str]
    work_mode: Optional[str]
    posted_date: Optional[datetime]
    apply_url: Optional[str]
    description: Optional[str]
    source: Optional[str]

class JobFilters(BaseModel):
    location: Optional[str] = None
    industry: Optional[str] = None
    experience_level: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    education_level: Optional[str] = None
    visa_status: Optional[str] = None
    work_mode: Optional[str] = None
    posted_within_days: Optional[int] = None
    company_size: Optional[str] = None
    q: Optional[str] = None

class ChatIn(BaseModel):
    message: str
    profile_id: Optional[int] = None
    job_id: Optional[int] = None

class ChatOut(BaseModel):
    reply: str
