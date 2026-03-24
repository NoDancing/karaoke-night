from fastapi import APIRouter, HTTPException
import yt_dlp

router = APIRouter()


@router.get("/search")
def search_youtube(q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f"ytsearch5:{q}", download=False)
    return [
        {
            "title": entry.get("title"),
            "url": f"https://www.youtube.com/watch?v={entry['id']}",
            "thumbnail": entry.get("thumbnail"),
            "channel": entry.get("channel") or entry.get("uploader"),
            "duration": entry.get("duration"),
        }
        for entry in (results.get("entries") or [])
        if entry and entry.get("id")
    ]
