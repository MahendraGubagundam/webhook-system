from fastapi import FastAPI, Request
from datetime import datetime

app = FastAPI()

received_events = []

@app.get("/")
def health_check():
    return {
        "service": "mock-receiver",
        "status": "running"
    }

@app.post("/webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": payload
    }

    received_events.append(log_entry)

    print("\n========== WEBHOOK RECEIVED ==========")
    print("Time:", log_entry["timestamp"])
    print("Payload:", payload)
    print("======================================\n")

    return {
        "status": "received",
        "timestamp": log_entry["timestamp"]
    }            
@app.get("/events")
def list_received_events():
    """
    Helpful debugging endpoint to view all received events
    """
    return {
        "count": len(received_events),
        "events": received_events
    }


@app.delete("/events")
def clear_events():
    """
    Reset mock receiver logs
    Useful for testing scenarios
    """
    received_events.clear()

    return {
        "message": "events cleared"
    }
