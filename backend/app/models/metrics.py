from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from app.core.db import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, nullable=True)
    task_id = Column(String, index=True)
    status = Column(String, default="queued")  # queued / success / failure
    duration = Column(Float, nullable=True)  # seconds
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
