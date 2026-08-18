import time
from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ==========================================
# 🔄 MANUAL DEMO SWITCH (TOGGLE HERE)
# ==========================================
# MODE A: Test Non-DSA (Naive) Performance

from naive_limiter import NaiveRateLimiter as ActiveLimiter
is_dsa_mode = False

# MODE B: Test Optimized DSA Performance (Uncomment below & comment above)

# from multi_strategy_limiter import MultiStrategyRateLimiter as ActiveLimiter
# is_dsa_mode = True


# ==========================================

app = FastAPI()

# Initialize the active limiter
limiter = ActiveLimiter(capacity=5, window_seconds=10)

class ConfigUpdate(BaseModel):
    capacity: int
    window_seconds: int
    strategy: str = "sliding_window"

@app.post("/api/request")
def handle_request(
    user_id: str = "demo_user",
    endpoint: str = "/api/standard",
    x_user_tier: str = Header(default="free"),
):
    effective_capacity = limiter.capacity

    if x_user_tier == "pro":
        effective_capacity *= 3
    elif x_user_tier == "enterprise":
        effective_capacity *= 10

    if endpoint == "/api/heavy-computation":
        effective_capacity = max(1, effective_capacity // 3)

    tracking_key = f"{user_id}:{endpoint}:{x_user_tier}"

    original_capacity = limiter.capacity
    limiter.capacity = effective_capacity
    allowed = limiter.allow_request(tracking_key)
    limiter.capacity = original_capacity

    if allowed:
        return {"status": 200, "message": "OK", "tier": x_user_tier, "endpoint": endpoint}
    return JSONResponse(
        status_code=429,
        content={"status": 429, "message": "Too Many Requests (Rate Limit Exceeded)"},
    )

@app.get("/api/status")
def get_status(
    user_id: str = "demo_user",
    endpoint: str = "/api/standard",
    x_user_tier: str = "free",
):
    tracking_key = f"{user_id}:{endpoint}:{x_user_tier}"
    # Check if active limiter has get_status method (Naive might not have it)
    if hasattr(limiter, "get_status"):
        return limiter.get_status(tracking_key)
    return {
        "current_count": len(getattr(limiter, "requests", {}).get(tracking_key, [])),
        "capacity": limiter.capacity,
        "window_seconds": limiter.window_seconds,
        "strategy": "naive_list_scan",
        "details": "Non-DSA Naive Mode Active"
    }

@app.post("/api/config")
def update_config(cfg: ConfigUpdate):
    if hasattr(limiter, "update_config"):
        limiter.update_config(cfg.capacity, cfg.window_seconds, cfg.strategy)
    else:
        limiter.capacity = cfg.capacity
        limiter.window_seconds = cfg.window_seconds
    return {"message": "Configuration updated successfully", **cfg.dict()}

@app.post("/api/reset")
def reset_limits():
    if hasattr(limiter, "reset"):
        limiter.reset()
    else:
        if hasattr(limiter, "requests"):
            limiter.requests.clear()
    return {"message": "All limits reset"}

@app.post("/api/benchmark")
def run_benchmark(num_requests: int = 5000):
    """
    Tests ONLY the currently active imported limiter module (DSA or Non-DSA)
    to show isolated time complexity on the UI.
    """
    test_key = "benchmark_user:/api/test:free"
    
    test_limiter = ActiveLimiter(capacity=10000, window_seconds=60)
    
    start_time = time.perf_counter()
    for _ in range(num_requests):
        test_limiter.allow_request(test_key)
    end_time = time.perf_counter()
    
    execution_time_ms = round((end_time - start_time) * 1000, 2)
    
    mode_label = "Optimized DSA (Deque O(1))" if is_dsa_mode else "Non-DSA (Naive List-Scan O(N))"
    
    return {
        "num_requests": num_requests,
        "mode": mode_label,
        "execution_time_ms": execution_time_ms
    }