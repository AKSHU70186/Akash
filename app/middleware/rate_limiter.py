from fastapi import Request, HTTPException
import time
from redis import Redis
import asyncio

redis_client = Redis(host='localhost', port=6379, db=0)

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.redis = redis_client

    async def check_rate_limit(self, client_id: str):
        current = int(time.time())
        key = f"rate_limit:{client_id}:{current // 60}"
        
        count = self.redis.incr(key)
        if count == 1:
            self.redis.expire(key, 60)
        
        if count > self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            ) 