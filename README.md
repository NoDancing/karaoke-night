# Karaoke Night

Simple interface for queuing and playing karaoke clips off of youtube.

## How This Works

- Host sets up on laptop
- Guests submit youtube URLs from their phone
- Host screen plays when it's time
- Background music fills silence between songs

## Tech

- FastAPI (Python)
- Playback via yt-dlp + ffmpeg

## Setup & Running

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

## API

- `POST /queue` — add a song `{ "url": "...", "singer": "..." }`
- `GET /queue` — list the queue
- `DELETE /queue/{id}` — remove a song
