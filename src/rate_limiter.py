"""
Rate Limiter & Quota Management for TEKLİF-Sim (v2.1.0).
Prevents Gemini API rate limit exhaustion using Sliding Window algorithm.
"""

import time
from collections import deque
from src.logger import logger

class APIRateLimiter:
    """
    Sliding window rate limiter for LLM API requests.
    Default limit: 5 requests per minute (Free Tier alignment).
    """
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps = deque()

    def acquire(self) -> bool:
        """
        Enforces rate limiting. Waits if rate limit is reached within window.
        """
        now = time.time()
        
        # Remove timestamps older than current window
        while self.timestamps and self.timestamps[0] <= now - self.window_seconds:
            self.timestamps.popleft()

        if len(self.timestamps) >= self.max_requests:
            sleep_time = (self.timestamps[0] + self.window_seconds) - now + 0.1
            if sleep_time > 0:
                logger.warning(
                    f"Rate limit reached ({self.max_requests} req/{self.window_seconds}s). "
                    f"Throttling API call for {sleep_time:.2f} seconds."
                )
                time.sleep(sleep_time)
                now = time.time()
                while self.timestamps and self.timestamps[0] <= now - self.window_seconds:
                    self.timestamps.popleft()

        self.timestamps.append(time.time())
        return True

# Singleton instance for Gemini API calls
gemini_rate_limiter = APIRateLimiter(max_requests=5, window_seconds=60)
