# iosxvv
# nigger.works
# https://github.com/iosviolador
import json
import time

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

app = FastAPI()

with open("config.json", "r") as f:
    config = json.load(f)

webhook = config.get("webhook_url", "")

_rate_log: dict[str, list[float]] = {}
max_requests = 2
ratelimit_time = 600


class WebhookPayload(BaseModel):
    title: str = ""
    description: str = ""
    color: int = 0xED4245
    thumbnail_url: str = ""


@app.get("/")
def root():
    return {"status": "online"}


@app.post("/api/send_wh_msg")
def send_wh_msg(payload: WebhookPayload, request: Request):
    ip = request.client.host
    now = time.time()
    hits = _rate_log.get(ip, [])
    hits = [t for t in hits if now - t < ratelimit_time]

    if len(hits) >= max_requests:
        raise HTTPException(status_code=403, detail="ratelimited try again later.")

    if not webhook:
        raise HTTPException(status_code=500, detail="webhook_url is empty in config.json")

    embed = {
        "title": payload.title,
        "description": payload.description,
        "color": payload.color,
    }
    if payload.thumbnail_url:
        embed["thumbnail"] = {"url": payload.thumbnail_url}

    resp = requests.post(webhook, json={"embeds": [embed]})

    if resp.status_code not in (200, 204):
        raise HTTPException(status_code=500, detail=f"Discord {resp.status_code}: {resp.text}")

    hits.append(now)
    _rate_log[ip] = hits
    return {"success": True}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=True)
