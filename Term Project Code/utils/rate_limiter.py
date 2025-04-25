import asyncio
import time
from typing import Callable, Any
import functools

class RateLimiter:
    """Rate limit function calls."""
    
    def __init__(self, calls: int, period: float):
        self.calls = calls
        self.period = period
        self.timestamps = []
    
    async def acquire(self):
        """Acquire permission to make call."""
        now = time.time()
        
        
        self.timestamps = [t for t in self.timestamps if now - t <= self.period]
        
        if len(self.timestamps) >= self.calls:
            sleep_time = self.timestamps[0] + self.period - now
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                self.timestamps.pop(0)
        
        self.timestamps.append(now)

def rate_limit(calls: int, period: float) -> Callable:
    """Decorator for rate limiting."""
    limiter = RateLimiter(calls, period)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            await limiter.acquire()
            return await func(*args, **kwargs)
        return wrapper
    return decorator