from fastapi import APIRouter
from ..services.ai_assistant import penguin_reply
from ..schemas import ChatIn, ChatOut

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat", response_model=ChatOut)
async def penguin_chat(payload: ChatIn):
    ctx = {"profile_id": payload.profile_id, "job_id": payload.job_id}
    reply = await penguin_reply(payload.message, ctx)
    return ChatOut(reply=reply)
