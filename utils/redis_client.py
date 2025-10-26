from typing import List, Dict, Any, Optional
import json
import asyncio
from config.settings import get_settings

try:
    import redis.asyncio as aioredis
except Exception:
    aioredis = None

settings = get_settings()

_redis: Optional["aioredis.Redis"] = None


def get_redis_url() -> str:
    return getattr(settings, "REDIS_URL", "redis://localhost:6379/0")


async def get_redis() -> "aioredis.Redis":
    global _redis
    if _redis is None:
        if aioredis is None:
            raise RuntimeError("redis.asyncio not available")
        _redis = aioredis.from_url(get_redis_url(), decode_responses=True)
    return _redis


async def push_message(conversation_id: str, message: Dict[str, Any], max_len: int = 200) -> None:
    r = await get_redis()
    key = f"chat:{conversation_id}"
    await r.rpush(key, json.dumps(message))
    await r.ltrim(key, -max_len, -1)
    # set TTL to keep recent context (adjustable)
    await r.expire(key, 60 * 60 * 24 * 7)  # 7 days


async def get_messages(conversation_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    r = await get_redis()
    key = f"chat:{conversation_id}"
    items = await r.lrange(key, -limit, -1)
    return [json.loads(i) for i in items] if items else []