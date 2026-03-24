from fastapi import APIRouter, HTTPException
import yt_dlp

router = APIRouter()


@router.get("/search")
def search_youtube(q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    if "karaoke" not in q.lower():
        q = q + " karaoke"
    ydl_opts = {
        "quiet": False,
        "extract_flat": True,
        "skip_download": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch10:{q}", download=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    if not results:
        raise HTTPException(status_code=500, detail="yt-dlp returned no results object")
    entries = [
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
    karaoke_entries = [e for e in entries if "karaoke" in (e["title"] or "").lower()]
    return karaoke_entries if karaoke_entries else entries
