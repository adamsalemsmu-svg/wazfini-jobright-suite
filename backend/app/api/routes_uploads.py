from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from ..api.deps import get_current_user, require_db
from ..models import User
from ..schemas import UserOut
from ..services.resume_parser import parse_resume_text

router = APIRouter(prefix="/upload", tags=["uploads"])


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(require_db),
):
    text = (await file.read()).decode(errors="ignore")
    parsed = parse_resume_text(text)

    user = db.get(User, current_user.id)
    if user is None:
        return {"parsed": parsed}

    if parsed.get("phone"):
        user.phone = parsed["phone"]
    if parsed.get("linkedin"):
        user.linkedin_url = parsed["linkedin"]
    if parsed.get("github"):
        user.github_url = parsed["github"]
    skills = parsed.get("skills") or []
    if skills:
        user.resume_skills = skills

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "parsed": parsed,
        "user": UserOut.model_validate(user).model_dump(),
    }
