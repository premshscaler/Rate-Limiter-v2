import os
import time
import uuid
import requests
import streamlit as st

# Read backend URL from environment variables or default to local FastAPI server
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

API_URL = f"{API_BASE}/api/request"
STATUS_URL = f"{API_BASE}/api/status"
CONFIG_URL = f"{API_BASE}/api/config"
RESET_URL = f"{API_BASE}/api/reset"
BENCHMARK_URL = f"{API_BASE}/api/benchmark"

st.set_page_config(page_title="Multi-Strategy Rate Limiter", page_icon="⚡", layout="centered")
st.title("⚡ Multi-Strategy Rate Limiter Gateway")
st.caption("Simulate Algorithms, User Tiers, and Endpoint Granularity with Modular DSA Cores")

# Generate one unique user_id per browser session
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())[:8]

# Sidebar Controls
st.sidebar.header("⚙️ Gateway Configuration")
strategy = st.sidebar.selectbox("Algorithm Strategy", ["sliding_window", "token_bucket", "fixed_window"])
capacity = st.sidebar.slider("Base Capacity (Max Requests)", 1, 30, 5)
window_sec = st.sidebar.slider("Window Size (Seconds)", 1, 60, 10)

st.sidebar.caption(f"🆔 Your session ID: `{st.session_state.user_id}`")

if st.sidebar.button("Apply Config", use_container_width=True):
    try:
        requests.post(CONFIG_URL, json={"capacity": capacity, "window_seconds": window_sec, "strategy": strategy})
        st.success("Config Applied Successfully!")
    except requests.exceptions.ConnectionError:
        st.error("Backend offline. Run: uvicorn main:app --reload")

if st.sidebar.button("Reset All Limits", use_container_width=True):
    try:
        requests.post(RESET_URL)
        st.info("State Cleared.")
    except requests.exceptions.ConnectionError:
        st.error("Backend offline.")

st.divider()

# Request Simulation Parameters
col1, col2 = st.columns(2)
user_tier = col1.selectbox("User Subscription Tier", ["free", "pro", "enterprise"])
target_endpoint = col2.selectbox("Target Endpoint", ["/api/standard", "/api/heavy-computation"])

c_btn1, c_btn2 = st.columns(2)
send_single = c_btn1.button("📤 Send Single Request", use_container_width=True)
send_burst = c_btn2.button("💥 Burst Test (10 requests)", use_container_width=True)


def fire_request():
    headers = {"x-user-tier": user_tier}
    params = {"user_id": st.session_state.user_id, "endpoint": target_endpoint}
    try:
        resp = requests.post(API_URL, params=params, headers=headers)
        if resp.status_code == 200:
            st.toast(f"200 OK [{user_tier.upper()} tier on {target_endpoint}]", icon="✅")
        else:
            st.toast("429 Too Many Requests (Rate Limited)", icon="🚫")
    except requests.exceptions.ConnectionError:
        st.error("Backend offline. Run: uvicorn main:app --reload")


if send_single:
    fire_request()
if send_burst:
    for _ in range(10):
        fire_request()
        time.sleep(0.02)

st.divider()

# Live Status Section
try:
    status_resp = requests.get(
        STATUS_URL,
        params={"user_id": st.session_state.user_id, "endpoint": target_endpoint},
        headers={"x-user-tier": user_tier},
    ).json()
    st.subheader(f"📊 Live Metrics ({status_resp.get('strategy', 'unknown').replace('_', ' ').title()})")
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Usage", status_resp.get("current_count", 0))
    m2.metric("Window Base Cap", status_resp.get("capacity", 0))
    m3.metric("Window Span", f"{status_resp.get('window_seconds', 0)}s")
    st.info(f"**Engine Details:** {status_resp.get('details', 'Active')}")
except Exception:
    st.warning("Waiting for FastAPI backend connection...")

st.divider()

# Performance Lab: Isolated Algorithm Benchmark Section
st.subheader("🧪 Performance Lab: Isolated Algorithm Benchmarking")
st.caption("Test the currently active backend module (Toggle imports in main.py to switch between Non-DSA and DSA).")

bench_col1, bench_col2 = st.columns([1, 2])
req_count = bench_col1.slider("Simulation Request Count", 1000, 10000, 5000, step=1000)
run_bench_btn = bench_col2.button("🚀 Run Active Module Test", use_container_width=True)

if run_bench_btn:
    with st.spinner(f"Executing test with {req_count} requests..."):
        try:
            bench_resp = requests.post(BENCHMARK_URL, params={"num_requests": req_count}).json()
            
            mode_name = bench_resp.get("mode", "Unknown")
            exec_time = bench_resp.get("execution_time_ms", 0)
            
            st.metric(label=f"Execution Time ({mode_name})", value=f"{exec_time} ms")
            
            # Dynamic check based on whether the active mode is DSA or Non-DSA
            if "DSA" in mode_name:
                st.success(f"✅ **{mode_name} Active:** Notice how fast the O(1) deque handles heavy volume without lag.")
            else:
                st.warning(f"⚠️ **{mode_name} Active:** Notice how the O(N) list scan takes significantly higher processing time.")
                
        except requests.exceptions.ConnectionError:
            st.error("Backend offline. Make sure uvicorn is running.")