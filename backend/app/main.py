import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum, UniqueConstraint
)
from sqlalchemy.orm import relationship, Session
from dotenv import load_dotenv
import httpx
import enum
import re

from .core.db import Base, engine, get_db


# -------------------- .env --------------------
load_dotenv()

# -------------------- CONFIG ------------------
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT")  # optional

# -------------------- MODELS ------------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    actions = relationship("JobAction", back_populates="user", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="resumes")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    job_key = Column(String(64), unique=True, index=True)  # stable id like "cap1"
    company = Column(String(255))
    title = Column(String(255))
    location = Column(String(255))
    mode = Column(String(64))       # Onsite/Remote/Hybrid
    posted = Column(String(64))     # "1 hour ago"
    salary = Column(String(128))
    seniority = Column(String(128))
    exp = Column(String(64))
    match = Column(Integer, default=90)
    perks = Column(String(512))     # "H1B Sponsored;Comp & Benefits"
    description = Column(Text)      # full JD text

class ActionType(str, enum.Enum):
    saved = "saved"
    liked = "liked"
    applied = "applied"

class JobAction(Base):
    __tablename__ = "job_actions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False)
    action = Column(SAEnum(ActionType), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Avoid duplicate entries for same (user, job, action)
    __table_args__ = (UniqueConstraint("user_id", "job_id", "action", name="uq_user_job_action"),)

    user = relationship("User", back_populates="actions")
    job = relationship("Job")

Base.metadata.create_all(bind=engine)

# Seed demo jobs once
def seed_jobs(db: Session):
    if db.query(Job).count() > 0:
        return
    demo = [
        Job(job_key="cap1", company="Capital One", title="Sr. Data Analyst – Enterprise Services",
            location="McLean, VA", mode="Onsite", posted="1 hour ago",
            salary="$99k/yr – $113k/yr", seniority="Mid, Senior Level", exp="2+ years exp",
            match=98, perks="Comp. & Benefits;H1B Sponsored",
            description="Analyze enterprise services datasets, build dashboards (Power BI/Tableau), SQL & Python; Snowflake preferred."),
        Job(job_key="cap2", company="Capital One", title="Manager, Data Analysis – Card Services",
            location="McLean, VA", mode="Onsite", posted="1 hour ago",
            salary="$158k/yr – $181k/yr", seniority="Mid, Senior Level", exp="6+ years exp",
            match=94, perks="Comp. & Benefits;H1B Sponsored",
            description="Lead analytics for card services; SQL, Python, stakeholder leadership, KPIs, storytelling."),
        Job(job_key="temu1", company="Temu", title="Data Engineer",
            location="United States", mode="Remote", posted="5 hours ago",
            salary="$100k/yr – $300k/yr", seniority="Mid Level", exp="3+ years exp",
            match=98, perks="H1B Sponsor Likely",
            description="Build ELT on Snowflake/DBT, Python, Airflow; performance tuning; cross-functional delivery.")
    ]
    for j in demo:
        db.add(j)
    db.commit()

# -------------------- SECURITY ----------------
bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> User:
    token = credentials.credentials
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise cred_exc
    except JWTError:
        raise cred_exc
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise cred_exc
    return user

# -------------------- SCHEMAS -----------------
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
    password: str = Field(min_length=6, max_length=128)
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

class TailorIn(BaseModel):
    resume_id: Optional[int] = None
    resume_content: Optional[str] = None
    job_description: str
    role_title: Optional[str] = "Tailored Resume"
    style: Optional[str] = "Action-oriented, quantified, ATS-friendly, concise."

class TailorOut(BaseModel):
    title: str
    tailored_content: str

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
    class Config: from_attributes = True

class JobActionIn(BaseModel):
    job_id: int
    action: ActionType

class CopilotIn(BaseModel):
    job_id: int
    question: str
    use_active_resume: bool = True  # if true, use most recent resume for grounding

class CopilotOut(BaseModel):
    answer: str

class AutofillIn(BaseModel):
    job_id: int
    resume_id: Optional[int] = None

class AutofillOut(BaseModel):
    fields: Dict[str, str]
    notes: str

# NEW: Search filters for UAE (Phase-2)
class UAEJobFilters(BaseModel):
    q: Optional[str] = None               # keyword
    location: Optional[str] = None        # Dubai, Abu Dhabi, ...
    work_mode: Optional[str] = None       # Onsite/Hybrid/Remote
    experience_level: Optional[str] = None # matches 'seniority' text
    job_type: Optional[str] = None        # maps to 'mode' in our demo model
    posted_within_days: Optional[int] = None  # not reliable with 'posted' text; ignored in demo
    salary_min: Optional[int] = None      # strings in demo; ignored
    salary_max: Optional[int] = None      # strings in demo; ignored
    exclude_h1b: bool = True              # remove H1B-mention jobs for Dubai context

# -------------------- APP ---------------------
app = FastAPI(title="Wazfini JobRight Suite API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- AUTH --------------------
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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username.lower()).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password.")
    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token)

@app.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)):
    return current

# -------------------- RESUMES -----------------
@app.get("/resumes", response_model=List[ResumeOut])
def list_resumes(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Resume)
        .filter(Resume.user_id == current.id)
        .order_by(Resume.updated_at.desc())
        .all()
    )

@app.post("/resumes", response_model=ResumeOut)
def create_resume(payload: ResumeIn, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = Resume(user_id=current.id, title=payload.title.strip(), content=payload.content)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.put("/resumes/{resume_id}", response_model=ResumeOut)
def update_resume(
    resume_id: int,
    payload: ResumeIn,
    current: User = Depends(get_current_user),
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
def delete_resume(resume_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Resume not found.")
    db.delete(item)
    db.commit()
    return

# -------------------- JOBS --------------------
@app.get("/jobs", response_model=List[JobOut])
def list_jobs(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    seed_jobs(db)
    return db.query(Job).order_by(Job.match.desc()).all()

@app.get("/jobs/{job_id}", response_model=JobOut)
def job_detail(job_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    j = db.query(Job).filter(Job.id == job_id).first()
    if not j:
        raise HTTPException(404, "Job not found.")
    return j

@app.post("/jobs/action")
def job_action(payload: JobActionIn, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # idempotent create
    existing = db.query(JobAction).filter(
        JobAction.user_id == current.id,
        JobAction.job_id == payload.job_id,
        JobAction.action == payload.action
    ).first()
    if existing:
        # toggle off if exists
        db.delete(existing)
        db.commit()
        state = "removed"
    else:
        # ensure job exists
        j = db.query(Job).filter(Job.id == payload.job_id).first()
        if not j:
            raise HTTPException(404, "Job not found.")
        db.add(JobAction(user_id=current.id, job_id=payload.job_id, action=payload.action))
        db.commit()
        state = "added"
    # return fresh counters
    counts = _user_action_counts(db, current.id)
    return {"state": state, "counts": counts}

def _user_action_counts(db: Session, user_id: int) -> Dict[str, int]:
    rows = db.query(JobAction.action).filter(JobAction.user_id == user_id).all()
    counts = {"saved": 0, "liked": 0, "applied": 0}
    for (a,) in rows:
        counts[str(a)] += 1
    return counts

@app.get("/jobs/counters")
def job_counters(current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _user_action_counts(db, current.id)

@app.get("/jobs/by_action/{action}", response_model=List[JobOut])
def jobs_by_action(action: ActionType, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    seed_jobs(db)
    ids = [
        ja.job_id for ja in db.query(JobAction).filter(
            JobAction.user_id == current.id,
            JobAction.action == action
        ).all()
    ]
    if not ids:
        return []
    items = db.query(Job).filter(Job.id.in_(ids)).order_by(Job.match.desc()).all()
    return items

# -------------------- NEW: UAE-style Job Search (Phase-2) -----------------------
@app.post("/jobs/search", response_model=List[JobOut])
def jobs_search(filters: UAEJobFilters, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    seed_jobs(db)
    q = db.query(Job)

    if filters.location:
        q = q.filter(Job.location.ilike(f"%{filters.location}%"))

    if filters.work_mode:
        q = q.filter(Job.mode.ilike(f"%{filters.work_mode}%"))

    if filters.experience_level:
        # seniority is free text like "Mid, Senior Level"
        q = q.filter(Job.seniority.ilike(f"%{filters.experience_level}%"))

    if filters.job_type:
        # our demo model doesn't have a separate job_type; mode is closest
        q = q.filter(Job.mode.ilike(f"%{filters.job_type}%"))

    if filters.q:
        kw = f"%{filters.q}%"
        q = q.filter(
            (Job.title.ilike(kw)) |
            (Job.description.ilike(kw)) |
            (Job.company.ilike(kw))
        )

    if filters.exclude_h1b:
        q = q.filter(~Job.perks.ilike("%H1B%"))

    # NOTE: posted_within_days & salary_min/max are not reliable in this demo schema (string fields)
    items = q.order_by(Job.match.desc()).all()
    return items

# -------------------- NEW: Resume Upload + Parse (Phase-2) ----------------------
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
async def upload_resume(file: UploadFile = File(...), current: User = Depends(get_current_user)):
    raw = await file.read()
    try:
        text = raw.decode(errors="ignore")
    except Exception:
        # if it's actually text already
        text = raw if isinstance(raw, str) else raw.decode("utf-8", errors="ignore")
    parsed = _parse_resume_text(text)
    return {"parsed": parsed}

# -------------------- NEW: Penguin (AI Assistant) (Phase-2) ---------------------
PENGUIN_SYSTEM = (
    "You are Penguin, a concise, practical AI assistant for job search in the UAE. "
    "Give actionable advice. Avoid legal guidance. If unsure, ask for context briefly."
)

@app.post("/assistant/chat", response_model=CopilotOut)
async def penguin_chat(payload: CopilotIn, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Gather context
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    active_resume = None
    if payload.use_active_resume:
        active_resume = (
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
            "title": active_resume.title if active_resume else None,
            "content": (active_resume.content[:3000] + "…") if active_resume and active_resume.content else None,
        },
    }

    messages = [
        {"role": "system", "content": PENGUIN_SYSTEM},
        {"role": "user", "content": f"Question: {payload.question}\n\nContext: {context}"},
    ]

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    if OPENAI_PROJECT:
        headers["OpenAI-Project"] = OPENAI_PROJECT

    try:
        async with httpx.AsyncClient(timeout=40.0) as client:
            r = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={"model": OPENAI_MODEL, "messages": messages, "temperature": 0.3},
            )
            r.raise_for_status()
            data = r.json()
            answer = data["choices"][0]["message"]["content"].strip()
            return CopilotOut(answer=answer)
    except httpx.HTTPError as e:
        raise HTTPException(500, f"Penguin error: {str(e)}")
