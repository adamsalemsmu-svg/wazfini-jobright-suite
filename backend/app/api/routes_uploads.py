from fastapi import APIRouter, UploadFile, File
from ..services.resume_parser import parse_resume_text

router = APIRouter(prefix="/upload", tags=["uploads"])

@router.post("/resume")
async def upload_resume(file: UploadFile = File(...)):
    text = (await file.read()).decode(errors="ignore")
    parsed = parse_resume_text(text)
    return {"parsed": parsed}
