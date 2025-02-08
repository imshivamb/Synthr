from redis import Redis
from app.core.config import settings
import json
from typing import Any, Optional

class RedisClient:
    def __init__(self):
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
        
    async def get(self, key: str) -> Optional[Any]:
        """ Get value from redis """
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in Redis with expiration"""
        try:
            return self.redis.setex(key, expire, json.dumps(value))
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
        
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
        
    async def clear_cache(self, pattern: str) -> bool:
        """Clear all keys matching pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return bool(self.redis.delete(*keys))
            return True
        except Exception as e:
            print(f"Redis clear cache error: {e}")
            return False

redis_client = RedisClient()
            