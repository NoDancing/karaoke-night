from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime
import yt_dlp
import json

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

queue: List[dict] = []
clients: set[WebSocket] = set()


async def broadcast():
    message = json.dumps(queue)
    for ws in list(clients):
        try:
            await ws.send_text(message)
        except Exception:
            clients.discard(ws)


@app.get("/host")
def host():
    return RedirectResponse(url="/static/host.html")


@app.get("/guest")
def guest():
    return RedirectResponse(url="/static/guest.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        await websocket.send_text(json.dumps(queue))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.discard(websocket)


class SongRequest(BaseModel):
    url: str
    singer: str


@app.post("/queue", status_code=201)
async def add_song(song: SongRequest):
    entry = {
        "id": str(uuid.uuid4()),
        "url": song.url,
        "singer": song.singer,
        "added_at": datetime.utcnow().isoformat(),
    }
    queue.append(entry)
    await broadcast()
    return entry


@app.get("/queue")
def get_queue():
    return queue


@app.delete("/queue/{song_id}", status_code=204)
async def remove_song(song_id: str):
    for i, entry in enumerate(queue):
        if entry["id"] == song_id:
            queue.pop(i)
            await broadcast()
            return
    raise HTTPException(status_code=404, detail="Song not found")


@app.get("/queue/current/stream")
def get_stream():
    if not queue:
        raise HTTPException(status_code=404, detail="Queue is empty")
    url = queue[0]["url"]
    ydl_opts = {"format": "best[ext=mp4]/best", "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {"stream_url": info["url"], "title": info.get("title", "")}
