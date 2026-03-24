# Karaoke Night

Simple interface for queuing and playing karaoke clips off of YouTube.

## How This Works

- Host sets up on a laptop or TV
- Guests scan a QR code to add songs from their phones
- Host screen plays each song in order via the YouTube IFrame player

## Tech

- FastAPI (Python)
- Playback via YouTube IFrame API

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
- Play each song via the embedded YouTube player
- Show the current singer's name
- Display upcoming songs
- Advance automatically when a video ends
- Display a QR code in the corner — guests scan it to open the submission page

## Testing

Install dev dependencies and run the test suite:

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

Tests cover all API endpoints and WebSocket broadcasting.

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
3. Install nginx and Certbot:
   ```bash
   sudo apt-get install -y nginx certbot python3-certbot-nginx
   ```
4. Write an nginx config at `/etc/nginx/sites-available/karaoke-night` that proxies port 80 → 8000, with WebSocket upgrade support for `/ws`. Set `server_name` to your domain.
5. Enable the config and reload nginx:
   ```bash
   sudo ln -sf /etc/nginx/sites-available/karaoke-night /etc/nginx/sites-enabled/
   sudo rm -f /etc/nginx/sites-enabled/default
   sudo nginx -t && sudo systemctl reload nginx
   ```
6. Get a free HTTPS cert (auto-renews):
   ```bash
   sudo certbot --nginx -d your-domain.com --non-interactive --agree-tos -m you@email.com
   ```
7. Clone the repo:
   ```bash
   git clone https://github.com/NoDancing/karaoke-night.git ~/karaoke-night
   ```
8. Add two secrets to GitHub (`Settings → Secrets → Actions`):
   - `EC2_HOST` — your domain
   - `EC2_SSH_KEY` — contents of your `.pem` key file

After that, every push to `main` deploys automatically.

## Guest Page

Guests open `http://localhost:8000/guest` on their phone. They enter their name and a YouTube URL, and it gets added to the queue immediately.
