from fastapi import APIRouter
from backend.config.history_store import load_history

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("/")
def get_history():
    return load_history()