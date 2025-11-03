from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .deps import get_db
from ..models.metrics import Metric

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    total = db.query(Metric).count()
    success = db.query(Metric).filter(Metric.status == "SUCCESS").count()
    failure = db.query(Metric).filter(Metric.status == "FAILURE").count()
    return {"total": total, "success": success, "failure": failure}
