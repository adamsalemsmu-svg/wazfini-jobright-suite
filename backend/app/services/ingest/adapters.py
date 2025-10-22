# app/services/ingest/adapters.py
from .base import BaseAdapter
from datetime import datetime
class MockAdapter(BaseAdapter):
    source = "mock"
    async def fetch(self, query: str = "", location: str = "Dubai"):
        return [{
            "title":"Data Engineer","company":"ExampleTech","location":location,
            "salary_low":18000,"salary_high":26000,"currency":"AED","job_type":"Full-time",
            "experience_level":"Senior","industry":"Tech","education_level":"Bachelor",
            "work_mode":"Hybrid","posted_date":datetime.utcnow(),
            "apply_url":"https://example.com/apply","description":"Snowflake, Python, SQL, ADF",
            "source": self.source,
        }]
ADAPTERS = [MockAdapter()]
