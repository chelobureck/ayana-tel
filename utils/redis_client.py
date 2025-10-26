from typing import List, Dict, Any, Optional
import json
import asyncio
from config.settings import get_settings

try:
    # Пробуем импортировать современный async API
    from redis.asyncio import Redis as AsyncRedis  # type: ignore
    import redis.asyncio as aioredis  # type: ignore
    IS_ASYNC_REDIS = True
except (ImportError, AttributeError):
    try:
        # Fallback для старых версий redis
        import redis  # type: ignore
        aioredis = redis
        AsyncRedis = None
        IS_ASYNC_REDIS = False
    except ImportError:
        aioredis = None
        AsyncRedis = None
        IS_ASYNC_REDIS = False

settings = get_settings()

_redis = None
_redis_is_async = None


def get_redis_url() -> str:
    return getattr(settings, "REDIS_URL", "redis://localhost:6379/0")


async def get_redis():
    """Получает клиент Redis"""
    global _redis, _redis_is_async
    if _redis is None:
        if aioredis is None:
            raise RuntimeError("redis not available. Install with: pip install 'redis[hiredis]'")
        
        if IS_ASYNC_REDIS:
            # Современный async API
            _redis = await aioredis.from_url(get_redis_url(), decode_responses=True)
            _redis_is_async = True
        else:
            # Старый sync API - создаем синхронный клиент
            _redis = aioredis.from_url(get_redis_url(), decode_responses=True)
            _redis_is_async = False
    
    return _redis, _redis_is_async


async def push_message(conversation_id: str, message: Dict[str, Any], max_len: int = 200) -> None:
    """Добавляет сообщение в Redis"""
    try:
        r, is_async = await get_redis()
        key = f"chat:{conversation_id}"
        msg_json = json.dumps(message)
        
        loop = asyncio.get_event_loop()
        
        def _push():
            r.rpush(key, msg_json)
            r.ltrim(key, -max_len, -1)
            r.expire(key, 60 * 60 * 24 * 7)  # 7 days
        
        if is_async:
            # Асинхронный API
            await r.rpush(key, msg_json)
            await r.ltrim(key, -max_len, -1)
            await r.expire(key, 60 * 60 * 24 * 7)  # 7 days
        else:
            # Синхронный API - выполняем в executor
            await loop.run_in_executor(None, _push)
    except Exception as e:
        # Если Redis недоступен, просто логируем ошибку
        print(f"Warning: Redis push failed: {e}")


async def get_messages(conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Получает сообщения из Redis"""
    try:
        r, is_async = await get_redis()
        key = f"chat:{conversation_id}"
        
        loop = asyncio.get_event_loop()
        
        def _get():
            items = r.lrange(key, -limit, -1)
            return [json.loads(i) for i in items] if items else []
        
        if is_async:
            # Асинхронный API
            items = await r.lrange(key, -limit, -1)
            return [json.loads(i) for i in items] if items else []
        else:
            # Синхронный API - выполняем в executor
            return await loop.run_in_executor(None, _get)
    except Exception as e:
        # Если Redis недоступен, возвращаем пустой список
        print(f"Warning: Redis get failed: {e}")
        return []