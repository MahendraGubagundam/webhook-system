from fastapi import FastAPI, Header, HTTPException
from typing import List

app = FastAPI()

webhooks = []

@app.get("/")
def home():
    return {"message": "Webhook Delivery System Running"}

@app.post("/webhooks")
def create_webhook(data: dict, x_user_id: str = Header(...)):
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
def list_webhooks(x_user_id: str = Header(...)):
    return [w for w in webhooks if w["user_id"] == x_user_id]


@app.delete("/webhooks/{webhook_id}")
def delete_webhook(webhook_id: int):
    global webhooks
    webhooks = [w for w in webhooks if w["id"] != webhook_id]
    return {"message": "webhook deleted"}


@app.patch("/webhooks/{webhook_id}/toggle")
def toggle_webhook(webhook_id: int):
    for w in webhooks:
        if w["id"] == webhook_id:
            w["active"] = not w["active"]
            return w

    raise HTTPException(status_code=404, detail="Webhook not found")
