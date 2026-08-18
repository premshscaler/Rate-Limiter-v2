import time

class NaiveRateLimiter:
    """
    Unoptimized Non-DSA baseline limiter using a plain Python list.
    Simulates O(N) full scans and unbounded memory growth.
    """
    def __init__(self, capacity: int, window_seconds: int):
        self.capacity = capacity
        self.window_seconds = window_seconds
        self.requests = {} # key -> list of timestamps

    def allow_request(self, key: str) -> bool:
        now = time.time()
        if key not in self.requests:
            self.requests[key] = []
        
        history = self.requests[key]
        
        # O(N) full-scan filtering across all historical records
        valid_requests = [ts for ts in history if ts > now - self.window_seconds]
        self.requests[key] = valid_requests

        if len(valid_requests) < self.capacity:
            self.requests[key].append(now)
            return True
        return False