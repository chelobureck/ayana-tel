"""
Скрипт для инициализации базы данных
Запустите этот скрипт перед первым запуском бота
"""
import asyncio
from models.base import engine, Base, async_session
from models.user import User
from models.chat import ChatMessage, ChildInfo


async def init_db():
    """Создает все таблицы в базе данных"""
    print("Создание таблиц в базе данных...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✓ Таблицы успешно созданы!")
    print("\nДоступные таблицы:")
    print("  - users")
    print("  - chat_messages")  
    print("  - child_info")
    print("\nБаза данных готова к использованию!")


if __name__ == "__main__":
    asyncio.run(init_db())

