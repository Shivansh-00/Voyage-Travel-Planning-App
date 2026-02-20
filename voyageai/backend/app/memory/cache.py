import json
import redis.asyncio as redis


class RedisCache:
    def __init__(self, redis_url: str):
        self._client = redis.from_url(redis_url, decode_responses=True)

    async def get_json(self, key: str):
        raw = await self._client.get(key)
        return json.loads(raw) if raw else None

    async def set_json(self, key: str, value, ttl: int = 900):
        await self._client.set(key, json.dumps(value), ex=ttl)
