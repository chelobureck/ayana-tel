from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.base import get_session
from fastapi import HTTPException, Header


async def get_current_user(
    x_user_id: Optional[int] = Header(None),
    session: Optional[AsyncSession] = None
) -> User:
    """
    Получает текущего пользователя по x_user_id из заголовка.
    Для упрощения возвращает дефолтного пользователя если заголовок не установлен.
    """
    if x_user_id is None:
        # Временный фиктивный пользователь для разработки
        return User(id=1, telegram_id=1)
    
    if session is None:
        # Fallback если сессия не предоставлена
        return User(id=1, telegram_id=x_user_id)
    
    result = await session.execute(select(User).where(User.telegram_id == x_user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        # Создаем нового пользователя если не существует
        user = User(telegram_id=x_user_id)
        session.add(user)
        await session.flush()
    
    return user


def get_current_user_sync(user_id: Optional[int]) -> User:
    """
    Синхронная версия для использования в телеграм боте.
    Создает временного пользователя для sessionless операций.
    """
    # Для telegram бота мы можем использовать простую заглушку
    user = User(id=1, telegram_id=user_id)
    return user

