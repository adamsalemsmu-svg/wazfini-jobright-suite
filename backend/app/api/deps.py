# backend/app/api/deps.py
from ..core.db import get_session

get_db = get_session
