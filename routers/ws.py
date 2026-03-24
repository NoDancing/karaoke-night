import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import state

router = APIRouter()


def _message():
    return json.dumps({"queue": state.queue, "title": state.event_title})


async def broadcast():
    message = _message()
    for ws in list(state.clients):
        try:
            await ws.send_text(message)
        except Exception:
            state.clients.discard(ws)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state.clients.add(websocket)
    try:
        await websocket.send_text(_message())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        state.clients.discard(websocket)
