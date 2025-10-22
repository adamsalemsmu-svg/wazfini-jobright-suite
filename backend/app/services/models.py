from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    name: Optional[str] = None

class Profile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    summary: Optional[str] = None

    experiences: List["Experience"] = Relationship(back_populates="profile")
    educations: List["Education"] = Relationship(back_populates="profile")
    skills: List["Skill"] = Relationship(back_populates="profile")

class Experience(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="profile.id")
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    profile: Profile = Relationship(back_populates="experiences")

class Education(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="profile.id")
    school: str
    degree: Optional[str] = None
    gpa: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    profile: Profile = Relationship(back_populates="educations")

class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profile_id: int = Field(foreign_key="profile.id")
    name: str
    profile: Profile = Relationship(back_populates="skills")

class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    company: str
    location: str
    salary_low: Optional[int] = None
    salary_high: Optional[int] = None
    currency: str = "AED"
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    industry: Optional[str] = None
    education_level: Optional[str] = None
    work_mode: Optional[str] = None
    posted_date: Optional[datetime] = None
    apply_url: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
