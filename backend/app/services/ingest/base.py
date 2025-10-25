# app/services/ingest/base.py
class BaseAdapter:
    source = "base"

    async def fetch(self, query: str = "", location: str = "Dubai"):
        raise NotImplementedError
