from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
import asyncio, json, uuid

app = FastAPI()

devices: Dict[str, WebSocket] = {}
pending: Dict[str, asyncio.Future] = {}

@app.get("/")
def health_check():
    return {"status": "ok", "devices": len(devices)}

@app.websocket("/ws/{device_id}")
async def ws_endpoint(ws: WebSocket, device_id: str):
    await ws.accept()
    devices[device_id] = ws
    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            req_id = msg.get("req_id")
            if req_id and req_id in pending and not pending[req_id].done():
                pending[req_id].set_result(msg)
    except WebSocketDisconnect:
        devices.pop(device_id, None)

@app.post("/cmd/{device_id}")
async def send_cmd(device_id: str, body: dict):
    if device_id not in devices:
        return {"ok": False, "error": "device offline"}
    req_id = str(uuid.uuid4())
    fut = asyncio.get_event_loop().create_future()
    pending[req_id] = fut

    await devices[device_id].send_text(json.dumps({
        "req_id": req_id,
        "action": body["action"],
        "args": body.get("args", {})
    }))

    try:
        result = await asyncio.wait_for(fut, timeout=30)
    except asyncio.TimeoutError:
        return {"ok": False, "error": "timeout"}
    finally:
        pending.pop(req_id, None)

    return {"ok": True, "result": result.get("data")}

@app.get("/devices")
async def list_devices():
    return {"devices": list(devices.keys())}
