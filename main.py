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
background_url: str | None = None


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


@app.get("/admin")
def admin():
    return RedirectResponse(url="/static/admin.html")


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


class ReorderRequest(BaseModel):
    ids: List[str]


@app.put("/queue/reorder", status_code=200)
async def reorder_queue(body: ReorderRequest):
    id_to_entry = {e["id"]: e for e in queue}
    if set(body.ids) != set(id_to_entry.keys()):
        raise HTTPException(status_code=400, detail="IDs do not match current queue")
    queue.clear()
    queue.extend(id_to_entry[i] for i in body.ids)
    await broadcast()
    return queue


class BackgroundUrlRequest(BaseModel):
    url: str


@app.put("/background/url", status_code=200)
def set_background_url(body: BackgroundUrlRequest):
    global background_url
    background_url = body.url
    return {"url": background_url}


@app.get("/background/url")
def get_background_url():
    return {"url": background_url}


@app.get("/background/stream")
def get_background_stream():
    if not background_url:
        raise HTTPException(status_code=404, detail="No background music URL set")
    ydl_opts = {"format": "bestaudio/best", "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(background_url, download=False)
    return {"stream_url": info["url"]}


@app.get("/queue/current/stream")
def get_stream():
    if not queue:
        raise HTTPException(status_code=404, detail="Queue is empty")
    url = queue[0]["url"]
    ydl_opts = {"format": "best[ext=mp4]/best", "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return {"stream_url": info["url"], "title": info.get("title", "")}
