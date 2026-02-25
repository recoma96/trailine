import json
import logging
from typing import Any
from contextlib import asynccontextmanager
from uuid import uuid4

import redis.asyncio as redis
from redis.asyncio import Redis

from trailine_api.settings import Settings

_logger = logging.getLogger(__name__)


class RedisCache:
    def __init__(self) -> None:
        self._client: Redis | None = None

    def get_client(self) -> Redis:
        """
        Redis 클라이언트를 Lazy-init로 생성해 반환한다.
        """
        if self._client is None:
            self._client = redis.from_url(
                Settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                health_check_interval=Settings.REDIS_HEALTH_CHECK_INTERVAL,
            )
        return self._client

    async def init(self) -> Redis:
        """
        FastAPI startup에서 호출해 Redis 연결을 확인한다.
        """
        client = self.get_client()
        await client.ping()
        _logger.info("Redis connected: %s", Settings.REDIS_URL)
        return client

    async def close(self) -> None:
        """
        FastAPI shutdown에서 호출해 Redis 연결을 종료한다.
        """
        if self._client is not None:
            await self._client.close()
            self._client = None
            _logger.info("Redis connection closed")

    async def get(self, key: str) -> str | None:
        return await self.get_client().get(key)

    async def set(self, key: str, value: str, ttl_seconds: int | None = None) -> bool:
        return await self.get_client().set(key, value, ex=ttl_seconds)

    async def delete(self, *keys: str) -> int:
        return await self.get_client().delete(*keys)

    async def exists(self, key: str) -> bool:
        return bool(await self.get_client().exists(key))

    async def ttl(self, key: str) -> int:
        return int(await self.get_client().ttl(key))

    async def set_json(
        self,
        key: str,
        value: dict[str, Any] | list[Any],
        ttl_seconds: int | None = None,
    ) -> bool:
        return await self.set(key, json.dumps(value, ensure_ascii=False), ttl_seconds=ttl_seconds)

    async def get_json(self, key: str) -> dict[str, Any] | list[Any] | None:
        raw = await self.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def acquire_lock(self, key: str, ttl_seconds: int = 30) -> str | None:
        token = uuid4().hex
        ok = await self.get_client().set(key, token, ex=ttl_seconds, nx=True)
        if ok:
            return token
        return None

    async def release_lock(self, key: str, token: str) -> bool:
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        result = await self.get_client().eval(script, 1, key, token)
        return result == 1

    @asynccontextmanager
    async def lock(self, key: str, ttl_seconds: int = 30):
        token = await self.acquire_lock(key, ttl_seconds=ttl_seconds)
        try:
            yield token
        finally:
            if token is not None:
                await self.release_lock(key, token)


cache = RedisCache()
