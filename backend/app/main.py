# backend/app/main.py

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, DateTime, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.orm import Session, relationship

from .core.db import Base, engine, get_db  # must exist in backend/app/core/db.py

# ------------------------------------------------------------------------------
# Security / Auth
# ------------------------------------------------------------------------------

pwd_context = PassLibContext = PasswordHasher = None  # keep linters calm
pwd_context = PasslibContext = PasswordHasher = None  # (optional hints for IDEs)

pwd_context = PasslibContext = PasswordHasher = None  # compatibility shim
pwd_context = PasslibContext = PasswordHasher = None

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=True)

def get_password_hash(raw: str) -> str:
    return pwd_context.hash(raw)

def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)

# ------------------------------------------------------------------------------
# Settings (from env)
# ------------------------------------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT")  # optional

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
ALGORITHM = "HS256"

from jose import jwt  # after constants to avoid flake8 circular hints

# ------------------------------------------------------------------------------
# SQLAlchemy Models
# ------------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="resumes")


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_key = Column(String, unique=True, index=True)  # for dedup/ingestion
    company = Column(String)
    title = Column[String]
    location = Column(String)
    mode = Column(String)      # Onsite/Hybrid/Remote
    posted = Column(String)    # e.g. "1 day ago"
    salary = Column(String)
    seniority = Column(String) # e.g. "Mid / Senior"
    exp = Column(String)
    match = Column(Integer, default=80)
    perks = Column(String)
    description = Column(String)


import enum

class ActionType(str, enum.Enum):
    saved = "saved"
    liked = "liked"
    applied = "applied"


class JobAction(Base):
    __tablename__ = "job_actions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), index=True, nullable=False)
    action = Column(SAEnum(ActionType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables (reset DB if schema changed)
Base.metadata.create_all(bind=engine)

# ------------------------------------------------------------------------------
# Pydantic Schemas
# ------------------------------------------------------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    email: EmailStr
    name: str = ""
    class Config:
        from_attributes = True

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = ""

class ResumeIn(BaseModel):
    title: str
    content: str

class ResumeOut(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class JobOut(BaseModel):
    id: int
    job_key: str
    company: str
    title: str
    location: str
    mode: str
    posted: str
    salary: str
    seniority: str
    exp: str
    match: int
    perks: str
    description: str
    class Config:
        from_attributes = True

class JobActionIn(BaseModel):
    job_id: int
    action: ActionType

class CopilotIn(BaseModel):
    job_id: Optional[int] = None
    question: str
    use_active_resume: bool = True

class CopilotOut(BaseModel):
    answer: str

class UAEJobFilters(BaseModel):
    q: Optional[str] = None
    location: Optional[str] = None
    work_mode: Optional[str] = None
    experience_level: Optional[str] = None
    job_type: Optional[str] = None
    posted_within_days: Optional[int] = None  # demo data uses strings; treated as hint
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    exclude_h1b: bool = True

# ------------------------------------------------------------------------------
# FastAPI App & CORS
# ------------------------------------------------------------------------------
# Determine CORS origins from environment variables
cors_origins_env = os.getenv("CORS_ORIGINS") or os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app = FastAPI(title="Wazfini JobRight Suite API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
        allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 
# ----------------------------------------------------------------------------
# Auth Helpers
# ------------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, os.getenv("JWT_SECRET", "dev-secret"), algorithm=ALGORITHM)

def get_db(token=Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token.credentials, os.getenv("JWT_SECRET", "dev-secret"), algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=403, detail="Not authenticated")
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return user

# ------------------------------------------------------------------------------
# Seed Demo Jobs
# ------------------------------------------------------------------------------

def seed_jobs(db: Session) -> None:
    if db.query(Job).count() > 0:
        return
    demo = [
        Job(
            job_key="cap1",
            company="Capital One",
            title="Sr. Data Analyst",
            location="McLean, VA",
            mode="Onsite",
            posted="1 day ago",
            salary="$120k",
            seniority="Senior",
            exp="5+ years",
            match=96,
            perks="Bonus; Healthcare",
            description="Build dashboards, SQL, analytics, stakeholder communication."
        ),
        Job(
            job_key="temu1",
            company="Temu",
            title="Data Engineer",
            location="United States",
            mode="Remote",
            posted="2 days ago",
            salary="$140k",
            seniority="Senior",
            exp="6+ years",
            match=92,
            perks="Stock; Remote",
            description="ETL pipelines, Spark, Databricks, data modeling."
        ),
        Job(
            job_key="dub1",
            company="Emirates NBD",
            title="Senior Data Engineer",
            location="Dubai, UAE",
            mode="Remote",
            posted="1 day ago",
            salary="AED 25k–35k/mo",
            seniority="Senior",
            exp="5+ years",
            match=99,
            perks="Housing Allowance; Medical",
            description="Azure-based data lake & analytics for banking."
        ),
    ]
    db.add_all(demo)
    db.commit()

# ------------------------------------------------------------------------------
# Auth Endpoints
# ------------------------------------------------------------------------------

@app.post("/auth/register", response_model=UserOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")
    user = User(
        email=payload.email.lower(),
        password_hash=get_password_hash(payload.password),
        name=payload.name or "",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username.lower()).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password.")
    return Token(access_token=create_access_token({"sub": str(user.id)}))

@app.get("/me", response_model=UserOut)
def me(current: User = Depends(get_db)):
    return current

# ------------------------------------------------------------------------------
# Resume Endpoints
# ------------------------------------------------------------------------------

@app.get("/resumes", response_model=List[ResumeOut])
def list_resumes(current: User = Depends(get_db), db: Session = Depends(get_db)):
    return (
        db.query(Resume)
        .filter(Resume.user_id == current.id)
        .order_by(Resume.updated_at.desc())
        .all()
    )

@app.post("/resumes", response_model=ResumeOut)
def create_resume(payload: ResumeIn, current: User = Depends(get_db), db: Session = Depends(get_db)):
    item = Resume(user_id=current.id, title=payload.title.strip(), content=payload.content)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.put("/resumes/{resume_id}", response_model=ResumeOut)
def update_resume(
    resume_id: int,
    payload: ResumeIn,
    current: User = Depends(get_db),
    db: Session = Depends(get_db),
):
    item = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Resume not found.")
    item.title = payload.title.strip()
    item.content = payload.content
    item.updated_at = datetime.utcnow()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.delete("/resumes/{resume_id}", status_code=204)
def delete_resume(resume_id: int, current: User = Depends(get_db), db: Session = Depends(get_db)):
    item = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Resume not found.")
    db.delete(item)
    db.commit()
    return

# ------------------------------------------------------------------------------
# Job Endpoints
# ------------------------------------------------------------------------------

@app.get("/jobs", response_model=List[JobOut])
def list_jobs(current: User = Depends(get_db), db: Session = Depends(get_db)):
    seed_jobs(db)
    return db.query(Job).order_by(Job.match.desc()).all()

@app.get("/jobs/{job_id}", response_model=JobOut)
def job_detail(job_id: int, current: User = Depends(get_db), db: Session = Depends(get_db)):
    j = db.query(Job).filter(Job.id == job_id).first()
    if not j:
        raise HTTPException(404, "Job not found.")
    return j

@app.post("/jobs/action")
def job_action(payload: JobActionIn, current: User = Depends(get_db), db: Session = Depends(get_db)):
    existing = db.query(JobAction).filter(
        JobAction.user_id == current.id,
        JobAction.job_id == payload.job_id,
        JobAction.action == payload.action,
    ).first()
    if existing:
        db.delete(existing)
        db.commit()
        state = "removed"
    else:
        j = db.query(Job).filter(Job.id == payload.job_id).first()
        if not j:
            raise HTTPException(404, "Job not found.")
        db.add(JobAction(user_id=current.id, job_id=payload.job_id, action=payload.action))
        db.commit()
        state = "added"
    return {"state": state, "counts": _user_action_counts(db, current.id)}

@app.get("/jobs/counters")
def job_counters(current: User = Depends(get_db), db: Session = Depends(get_db)):
    return _user_action_counts(db, current.id)

@app.get("/jobs/by_action/{action}", response_model=List[JobOut])
def jobs_by_action(action: ActionType, current: User = Depends(get_db), db: Session = Depends(get_db)):
    seed_jobs(db)
    ids = [
        ja.job_id
        for ja in db.query(JobAction).filter(
            JobAction.user_id == current.id, JobAction.action == action
        ).all()
    ]
    if not ids:
        return []
    return db.query(Job).filter(Job.id.in_(ids)).order_by(Job.match.desc()).all()

def _user_action_counts(db: Session, user_id: int) -> Dict[str, int]:
    rows = db.query(JobAction.action).filter(JobAction.user_id == user_id).all()
    out = {"saved": 0, "liked": 0, "applied": 0}
    for (a,) in rows:
        out[str(a)] += 1
    return out

# ------------------------------------------------------------------------------
# UAE-style Job Search
# ------------------------------------------------------------------------------

@app.post("/jobs/search", response_model=List[JobOut])
def jobs_search(
    filters: UAEJobFilters,
    current: User = Depends(get_db),
    db: Session = Depends(get_db),
):
    seed_jobs(db)
    q = db.query(Job)

    if filters.location:
        q = q.filter(Job.location.ilike(f"%{filters.location}%"))
    if filters.work_mode:
        q = q.filter(Job.mode.ilike(f"%{filters.work_mode}%"))
    if filters.experience_level:
        q = q.filter(Job.seniority.ilike(f"%{filters.experience_level}%"))
    if filters.job_type:
        q = q.filter(Job.mode.ilike(f"%{filters.job_type}%"))
    if filters.q:
        kw = f"%{filters.q}%"
        q = q.filter(
            (Job.title.ilike(kw)) | (Job.description.ilike(kw)) | (Job.company.ilike(kw))
        )
    if filters.exclude_h1b:
        q = q.filter(~Job.perks.ilike("%H1B%"))

    return q.order_by(Job.match.desc()).all()

# ------------------------------------------------------------------------------
# Resume Upload + Parse
# ------------------------------------------------------------------------------

def _parse_resume_text(text: str) -> Dict[str, Optional[str]]:
    email = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone = re.search(r"\+?\d[\d\s\-]{7,}\d", text)
    linkedin = re.search(r"https?://(?:www\.)?linkedin\.com/\S+", text)
    github = re.search(r"https?://(?:www\.)?github\.com/\S+", text)
    skills = sorted(set(re.findall(
        r"\b(Python|SQL|Snowflake|Power BI|Tableau|Azure|Databricks|ETL|ELT|Spark)\b",
        text, re.I
    )))
    return {
        "email": email.group(0) if email else None,
        "phone": phone.group(0) if phone else None,
        "linkedin": linkedin.group(0) if linkedin else None,
        "github": github.group(0) if github else None,
        "skills": skills,
    }

@app.post("/upload/resume")
async def upload_resume(file: UploadFile = File(...), current: User = Depends(get_db)):
    raw = await file.read()
    text = raw.decode(errors="ignore") if isinstance(raw, (bytes, bytearray)) else str(raw)
    return {"parsed": _parse_resume_text(text)}

# ------------------------------------------------------------------------------
# Penguin Assistant
# ------------------------------------------------------------------------------

PENGUIN_SYSTEM = (
    "You are Penguin, a concise, practical AI assistant for job search in the UAE. "
    "Give actionable, specific advice. Avoid legal guidance. If details are missing, ask a brief follow-up."
)

@app.post("/assistant/chat", response_model=CopilotOut)
async def assistant_chat(
    payload: CopilotIn,
    current: User = Depends(get_db),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    resume = None
    if payload.use_active_resume:
        resume = (
            db.query(Resume)
            .filter(Resume.user_id == current.id)
            .order_by(Resume.updated_at.desc())
            .first()
        )

    context = {
        "user": {"id": current.id, "email": current.email, "name": current.name},
        "job": {
            "id": job.id if job else None,
            "title": job.title if job else None,
            "company": job.company if job else None,
            "location": job.location if job else None,
            "mode": job.mode if job else None,
            "seniority": job.seniority if job else None,
            "description": (job.description[:1200] + "…") if job and job.description else None,
        },
        "resume": {
            "title": resume.title if resume else None,
            "content": (resume.content[:3000] + "…") if resume and resume.content else None,
        },
    }

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    if OPENAI_PROJECT:
        headers["OpenAI-Project"] = OPENAI_PROJECT

    try:
        async with httpx.AsyncClient(timeout=40.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={"model": OPENAI_MODEL, "messages": [
                    {"role": "system", "content": PENGUIN_SYSTEM},
                    {"role": "user", "content": f"Question: {payload.question}\n\nContext: {context}"},
                ], "temperature": 0.3},
            )
            resp.raise_for_status()
            data = resp.json()
            answer = data["choices"][0]["message"]["content"]
            return CopilotOut(answer=answer)
    except httpx.HTTPError as ex:
        raise HTTPException(status_code=500, detail=f"Penguin error: {ex}")

# Optional alias for legacy clients
@app.post("/tailor", response_model=CopilotOut)
async def tailor_alias(
    payload: CopilotIn,
    current: User = Depends(get_db),
    db: Session = Depends(get_db),
):
    return await assistant_chat(payload, current=current, db=db)
