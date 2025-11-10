from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from .deps import get_db
from ..models.metrics import Metric

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    total = db.query(Metric).count()
    success = db.query(Metric).filter(Metric.status == "SUCCESS").count()
    failure = db.query(Metric).filter(Metric.status == "FAILURE").count()
    avg_duration = db.query(func.avg(Metric.duration)).scalar() or 0
    return {"total": total, "success": success, "failure": failure, "avg_duration": avg_duration}

@router.get("/user/{user_id}")
def get_user_summary(user_id: int, db: Session = Depends(get_db)):
    total = db.query(Metric).filter(Metric.user_id == user_id).count()
    success = db.query(Metric).filter(Metric.user_id == user_id, Metric.status == "SUCCESS").count()
    failure = db.query(Metric).filter(Metric.user_id == user_id, Metric.status == "FAILURE").count()
    avg_duration = db.query(func.avg(Metric.duration)).filter(Metric.user_id == user_id).scalar() or 0
    return {"user_id": user_id, "total": total, "success": success, "failure": failure, "avg_duration": avg_duration}
