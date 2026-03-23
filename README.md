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

## Host Screen

Open `http://localhost:8000/host` on the screen guests will watch. It will:
- Use yt-dlp to extract a direct stream URL for each song
- Play video natively in the browser (no YouTube embed)
- Show the current singer's name
- Display upcoming songs
- Advance automatically when a video ends
- Wake up every 10 seconds when the queue is empty
- Displays a QR code in the corner — guests scan it to open the submission page

## Admin Controls

Open `http://localhost:8000/admin` on the host's device. Controls:
- **Skip** — removes the current song and advances playback
- **↑ / ↓** — reorder upcoming songs
- **✕** — delete any song from the queue

All changes are reflected on the host screen and guest pages instantly.

## Real-time Updates

All pages stay in sync via WebSocket (`/ws`). When a song is added or removed:
- The host screen's "Up Next" list updates instantly
- Guests see their live position in the queue after submitting

## Guest Page

Guests open `http://localhost:8000/guest` on their phone. They enter their name and a YouTube URL, and it gets added to the queue immediately.
