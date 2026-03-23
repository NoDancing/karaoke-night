from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uuid
from datetime import datetime

app = FastAPI()

queue: List[dict] = []


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
