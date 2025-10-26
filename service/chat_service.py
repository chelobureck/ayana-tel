from typing import List, Dict, Any, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models.chat import ChatMessage, ChildInfo
from models.user import User
from utils.redis_client import push_message, get_messages
from utils.extractor import extract_child_info


class ChatService:
    @staticmethod
    async def save_message_db(session: AsyncSession, conversation_id: str, sender: str, text: str, user_id: Optional[int] = None) -> ChatMessage:
        msg = ChatMessage(
            conversation_id=conversation_id,
            sender=sender,
            text=text,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        session.add(msg)
        await session.flush()
        return msg

    @staticmethod
    async def push_to_redis(conversation_id: str, sender: str, text: str, meta: Optional[Dict[str, Any]] = None):
        message = {"sender": sender, "text": text, "meta": meta or {}, "ts": datetime.utcnow().isoformat()}
        await push_message(conversation_id, message)

    @staticmethod
    async def get_context(conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        return await get_messages(conversation_id, limit=limit)

    @staticmethod
    async def extract_and_save_child_info(session: AsyncSession, user: User, text: str) -> Optional[ChildInfo]:
        data = extract_child_info(text)
        if not data:
            return None

        # find existing ChildInfo for user or create new
        q = await session.execute(select(ChildInfo).where(ChildInfo.user_id == user.id))
        child = q.scalars().first()
        if child is None:
            child = ChildInfo(
                user_id=user.id,
                name=data.get("name"),
                age=data.get("age"),
                additional=data.get("additional") or {},
                updated_at=datetime.utcnow()
            )
            session.add(child)
        else:
            # update fields if present
            changed = False
            if data.get("name"):
                child.name = data["name"]
                changed = True
            if data.get("age"):
                child.age = data["age"]
                changed = True
            if data.get("additional"):
                existing = child.additional or {}
                existing.update(data["additional"])
                child.additional = existing
                changed = True
            if changed:
                child.updated_at = datetime.utcnow()
                await session.flush()
        return child