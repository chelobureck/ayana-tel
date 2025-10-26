from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.chat import ChatMessage
from models.base import get_session
from utils.auth import get_current_user
from service.chat_service import ChatService
from schemas import (
    # создайте минимальные схемы в schemas/chat.py (ниже)
)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/send")
async def send_message(
    conversation_id: str,
    text: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Приём сообщения от пользователя:
    - сохраняет в БД (ChatMessage)
    - пушит в Redis (контекст)
    - запускает извлечение данных о ребёнке и сохраняет ChildInfo
    """
    if not conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id required")
    # save DB message
    msg = await ChatService.save_message_db(session, conversation_id, "user", text, user_id=current_user.id)
    # push to redis for context
    await ChatService.push_to_redis(conversation_id, "user", text, meta={"id": msg.id})
    # try extract child info
    await ChatService.extract_and_save_child_info(session, current_user, text)
    # flush/commit
    await session.commit()
    return {"ok": True, "message_id": msg.id}


@router.get("/history")
async def history(conversation_id: str, limit: int = 100):
    data = await ChatService.get_context(conversation_id, limit=limit)
    return {"conversation_id": conversation_id, "messages": data}