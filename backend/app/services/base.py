from typing import List, Dict

class BaseAdapter:
    source: str = "base"
    async def fetch(self, query: str = "", location: str = "Dubai") -> List[Dict]:
        raise NotImplementedError
