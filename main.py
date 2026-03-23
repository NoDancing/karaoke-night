from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime
import yt_dlp

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

queue: List[dict] = []


@app.get("/host")
def host():
    return RedirectResponse(url="/static/host.html")


@app.get("/guest")
def guest():
    return RedirectResponse(url="/static/guest.html")


class SongRequest(BaseModel):
    url: str
    singer: str


@app.post("/queue", status_code=201)
def add_song(song: SongRequest):
    entry = {
        "id": str(uuid.uuid4()),
        "url": song.url,
        "singer": song.singer,
        "added_at": datetime.utcnow().isoformat(),
    }
    queue.append(entry)
    return entry


@app.get("/queue")
def get_queue():
    return queue


@app.delete("/queue/{song_id}", status_code=204)
def remove_song(song_id: str):
    for i, entry in enumerate(queue):
        if entry["id"] == song_id:
            queue.pop(i)
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
