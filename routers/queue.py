import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import state
from routers.ws import broadcast

router = APIRouter()


class SongRequest(BaseModel):
    url: str
    singer: str


class ReorderRequest(BaseModel):
    ids: List[str]


@router.post("/queue", status_code=201)
async def add_song(song: SongRequest):
    entry = {
        "id": str(uuid.uuid4()),
        "url": song.url,
        "singer": song.singer,
        "added_at": datetime.utcnow().isoformat(),
    }
    state.queue.append(entry)
    await broadcast()
    return entry


@router.get("/queue")
def get_queue():
    return state.queue


@router.delete("/queue/{song_id}", status_code=204)
async def remove_song(song_id: str):
    for i, entry in enumerate(state.queue):
        if entry["id"] == song_id:
            state.queue.pop(i)
            await broadcast()
            return
    raise HTTPException(status_code=404, detail="Song not found")


@router.put("/queue/reorder", status_code=200)
async def reorder_queue(body: ReorderRequest):
    id_to_entry = {e["id"]: e for e in state.queue}
    if set(body.ids) != set(id_to_entry.keys()):
        raise HTTPException(status_code=400, detail="IDs do not match current queue")
    state.queue.clear()
    state.queue.extend(id_to_entry[i] for i in body.ids)
    await broadcast()
    return state.queue


class TitleRequest(BaseModel):
    title: str


@router.get("/title")
def get_title():
    return {"title": state.event_title}


@router.put("/title")
async def set_title(body: TitleRequest):
    if not body.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    state.event_title = body.title.strip()
    await broadcast()
    return {"title": state.event_title}
