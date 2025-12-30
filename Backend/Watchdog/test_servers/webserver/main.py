from fastapi import FastAPI, HTTPException, status, Response
import uvicorn
import time
import random
import os

app = FastAPI()

# 1. Normal Scenario: Basic Health Check
@app.get("/")
def read_root():
    return {"message": "Server is running normally"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "watchdog-test-server"}

# 2. Normal Scenario: Data Retrieval
@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id < 0:
         raise HTTPException(status_code=400, detail="User ID cannot be negative")
    if user_id == 999:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "name": f"User_{user_id}", "active": True}

# 3. Timeout/Latency Scenario: Simulate slow response
@app.get("/slow")
def slow_response(delay: int = 3):
    """Simulates a slow response. Default delay is 3 seconds."""
    time.sleep(delay)
    return {"status": "completed", "delay": delay}

# 4. Error Scenario: Internal Server Error (500)
@app.get("/error")
def trigger_error():
    """Simulates an unexpected server error."""
    raise HTTPException(status_code=500, detail="Simulated Internal Server Error")

# 5. Error Scenario: Service Unavailable (503)
@app.get("/maintenance")
def maintenance_mode():
    """Simulates service being down for maintenance."""
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Service is currently under maintenance"
    )

# 6. Flaky/Unstable Scenario: Randomly fails
@app.get("/unstable")
def unstable_service():
    """Simulates a flaky service that fails 50% of the time."""
    if random.choice([True, False]):
        raise HTTPException(status_code=500, detail="Random failure occurred")
    return {"status": "lucky", "message": "Request succeeded"}

# 7. Security Scenario: Unauthorized (401)
@app.get("/protected")
def protected_route():
    """Simulates a protected route requiring authentication."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication credentials were not provided"
    )

if __name__ == "__main__":
    # Allow port to be configured via environment variable, defaulting to 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)