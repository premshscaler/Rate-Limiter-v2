from collections import defaultdict, deque
import time

class PureSlidingWindowLimiter:
    """
    Pure DSA implementation focusing strictly on Sliding Window using a deque.
    Provides O(1) amortized left pops and constant time checks.
    """
    def __init__(self, capacity: int, window_seconds: int):
        self.capacity = capacity
        self.window_seconds = window_seconds
        self.user_requests = defaultdict(deque)

    def allow_request(self, key: str) -> bool:
        now = time.time()
        q = self.user_requests[key]
        
        # O(1) left pop eviction of expired timestamps
        while q and q[0] <= now - self.window_seconds:
            q.popleft()
            
        if len(q) < self.capacity:
            q.append(now)
            return True
        return False

    def reset(self):
        self.user_requests.clear()