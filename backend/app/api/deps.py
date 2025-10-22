from fastapi import Depends
from ..core.db import get_session

get_db = get_session
