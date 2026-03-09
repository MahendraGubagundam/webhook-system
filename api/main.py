import redis
import json
from fastapi import FastAPI, Header, HTTPException
from typing import Optional

app = FastAPI()

# Redis connection
r = redis.Redis(host="redis", port=6379, decode_responses=True)

# In-memory storage for webhooks
webhooks = []

# Supported events
VALID_EVENTS = [
    "request.created",
    "request.updated",
    "request.deleted"
]

# Default rate limit
rate_limit = {"limit": 10}

@app.get("/")
def home():
    return {"message": "Webhook Delivery System Running"}

@app.post("/webhooks")
def create_webhook(data: dict, x_user_id: str = Header(...)):
    for event in data["event_types"]:
        if event not in VALID_EVENTS:
            raise HTTPException(status_code=400, detail="Invalid event type")
    webhook = {
        "id": len(webhooks) + 1,
        "user_id": x_user_id,
        "url": data["url"],
        "event_types": data["event_types"],
        "active": True
    }
    webhooks.append(webhook)
    return webhook

@app.get("/webhooks")
def list_webhooks(
        x_user_id: str = Header(...),
        status: Optional[str] = None):
    result = [w for w in webhooks if w["user_id"] == x_user_id]
    if status == "active":
        result = [w for w in result if w["active"]]
    if status == "disabled":
        result = [w for w in result if not w["active"]]
    return result

@app.put("/webhooks/{webhook_id}")
def update_webhook(webhook_id: int, data: dict, x_user_id: str = Header(...)):
    for webhook in webhooks:
        if webhook["id"] == webhook_id and webhook["user_id"] == x_user_id:
            if "url" in data:
                webhook["url"] = data["url"]
            if "event_types" in data:
                for event in data["event_types"]:
                    if event not in VALID_EVENTS:
                        raise HTTPException(status_code=400, detail="Invalid event")
                webhook["event_types"] = data["event_types"]
            return webhook
    raise HTTPException(status_code=404, detail="Webhook not found")

@app.delete("/webhooks/{webhook_id}")
def delete_webhook(webhook_id: int, x_user_id: str = Header(...)):
    global webhooks
    webhooks = [
        w for w in webhooks
        if not (w["id"] == webhook_id and w["user_id"] == x_user_id)
    ]
    return {"message": "Webhook deleted"}

@app.patch("/webhooks/{webhook_id}/toggle")
def toggle_webhook(webhook_id: int, x_user_id: str = Header(...)):
    for webhook in webhooks:
        if webhook["id"] == webhook_id and webhook["user_id"] == x_user_id:
            webhook["active"] = not webhook["active"]
            return webhook

    raise HTTPException(status_code=404, detail="Webhook not found")

@app.post("/events")
def publish_event(event: dict):
    if event["event_type"] not in VALID_EVENTS:
        raise HTTPException(status_code=400, detail="Invalid event type")
    deliveries = 0
    for webhook in webhooks:
        if (
            webhook["user_id"] == event["user_id"]
            and webhook["active"]
            and event["event_type"] in webhook["event_types"]
        ):
            job = {
                "user_id": event["user_id"],
                "url": webhook["url"],
                "event": event
            }
            r.lpush("delivery_queue", json.dumps(job))
            deliveries += 1
    return {"queued_deliveries": deliveries}


@app.get("/internal/rate-limit")
def get_rate_limit():
    return rate_limit

@app.post("/internal/rate-limit")
def update_rate_limit(data: dict):
    if "limit" not in data:
        raise HTTPException(status_code=400, detail="limit required")
    rate_limit["limit"] = data["limit"]
    r.set("rate_limit", data["limit"])
    return {"new_rate_limit": data["limit"]}
