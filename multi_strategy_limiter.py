from collections import defaultdict, deque
import time

class MultiStrategyRateLimiter:
    """
    Comprehensive rate limiter supporting Sliding Window, Token Bucket, and Fixed Window.
    """
    def __init__(self, capacity: int, window_seconds: int, strategy: str = "sliding_window"):
        self.capacity = capacity
        self.window_seconds = window_seconds
        self.strategy = strategy
        self.user_requests = defaultdict(deque)
        self.token_buckets = {}

    def allow_request(self, key: str) -> bool:
        now = time.time()

        if self.strategy == "sliding_window":
            q = self.user_requests[key]
            while q and q[0] <= now - self.window_seconds:
                q.popleft()
            if len(q) < self.capacity:
                q.append(now)
                return True
            return False

        elif self.strategy == "token_bucket":
            if key not in self.token_buckets:
                self.token_buckets[key] = [float(self.capacity), now]
            tokens, last_time = self.token_buckets[key]
            elapsed = now - last_time
            refill_rate = self.capacity / self.window_seconds
            tokens = min(float(self.capacity), tokens + elapsed * refill_rate)
            if tokens >= 1.0:
                tokens -= 1.0
                self.token_buckets[key] = [tokens, now]
                return True
            self.token_buckets[key] = [tokens, now]
            return False

        elif self.strategy == "fixed_window":
            window_key = int(now // self.window_seconds)
            q = self.user_requests[key]
            while q and q[0] != window_key:
                q.popleft()
            current_count = sum(1 for w in q if w == window_key)
            if current_count < self.capacity:
                q.append(window_key)
                return True
            return False

        return False

    def get_status(self, key: str) -> dict:
        now = time.time()
        if self.strategy == "sliding_window":
            q = self.user_requests[key]
            while q and q[0] <= now - self.window_seconds:
                q.popleft()
            return {
                "current_count": len(q),
                "capacity": self.capacity,
                "window_seconds": self.window_seconds,
                "strategy": self.strategy,
                "details": [round(now - ts, 2) for ts in q],
            }
        elif self.strategy == "token_bucket":
            if key not in self.token_buckets:
                self.token_buckets[key] = [float(self.capacity), now]
            tokens, _ = self.token_buckets[key]
            return {
                "current_count": round(self.capacity - tokens, 2),
                "capacity": self.capacity,
                "window_seconds": self.window_seconds,
                "strategy": self.strategy,
                "details": f"Tokens remaining: {round(tokens, 2)}",
            }
        else:
            window_key = int(now // self.window_seconds)
            q = self.user_requests[key]
            current_count = sum(1 for w in q if w == window_key)
            return {
                "current_count": current_count,
                "capacity": self.capacity,
                "window_seconds": self.window_seconds,
                "strategy": self.strategy,
                "details": "Fixed window counter active",
            }

    def update_config(self, capacity: int, window_seconds: int, strategy: str):
        self.capacity = capacity
        self.window_seconds = window_seconds
        self.strategy = strategy
        self.user_requests.clear()
        self.token_buckets.clear()

    def reset(self):
        self.user_requests.clear()
        self.token_buckets.clear()