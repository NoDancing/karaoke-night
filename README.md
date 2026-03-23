# Karaoke Night

Simple interface for queuing and playing karaoke clips off of youtube.

## How This Works

- Host sets up on laptop

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

## Testing

Install dev dependencies and run the test suite:

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

Tests cover all API endpoints and WebSocket broadcasting.

## Background Music

On the admin page, paste a YouTube URL into the Background Music field and hit Save. The host screen will play it as audio-only whenever the queue is empty, and stop automatically when the next singer's video starts.

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

## Deployment

The app runs on EC2 behind Docker. On every push to `main`, GitHub Actions builds the image, pushes it to GHCR, and deploys to EC2 automatically.

### First-time EC2 setup

1. Launch a t3.small Ubuntu 22.04 instance, open ports 22, 80, and 443
2. SSH in and install Docker:
   ```bash
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker ubuntu
   ```
3. Clone the repo:
   ```bash
   git clone https://github.com/NoDancing/karaoke-night.git ~/karaoke-night
   ```
4. Add two secrets to GitHub (`Settings → Secrets → Actions`):
   - `EC2_HOST` — your EC2 public IP or domain
   - `EC2_SSH_KEY` — contents of your `.pem` key file

After that, every push to `main` deploys automatically.

## Guest Page

Guests open `http://localhost:8000/guest` on their phone. They enter their name and a YouTube URL, and it gets added to the queue immediately.
