# Technical Decisions

## 001 — YouTube Playback Method
**Decision:** YouTube IFrame API
**Alternatives considered:** yt-dlp + ffmpeg (see `ytdlp-playback` branch), youtube-dl
**Why:** The IFrame API is reliable, requires no server-side stream extraction, and works on any YouTube video without bot detection issues. The yt-dlp approach was attempted but abandoned due to YouTube's n-challenge and PO token requirements on EC2 IPs making it unreliable across all videos.

## 002 — Real-time Updates
**Decision:** WebSockets
**Alternatives considered:** Server-Sent Events, polling
**Why:** Queue updates need to be instant and bidirectional. SSE is one-way. Polling is inefficient and feels laggy in a live party setting.

## 003 — State Management
**Decision:** In-memory Python list
**Alternatives considered:** Redis, SQLite
**Why:** No persistence needed — the queue lives and dies with the party. Redis adds operational complexity with no real benefit at this scale.

## 004 — Backend Framework
**Decision:** FastAPI
**Alternatives considered:** Flask, Django
**Why:** Native async support pairs well with WebSockets. Lightweight enough for this project. Flask's WebSocket support is awkward; Django is overkill.

## 014 — Modular project structure
**Decision:** Split main.py into `state.py` + `routers/` (pages, queue, ws)
**Alternatives considered:** Keep everything in main.py
**Why:** A single-file backend caused repeated add/remove cycles as features changed. Splitting by concern means adding or removing a feature is isolated to one file. `state.py` holds shared in-memory state so routers don't need to import each other circularly.

## 005 — Frontend
**Decision:** Vanilla HTML/JS
**Alternatives considered:** React, HTMX
**Why:** No build step, easy to read and modify. React is overkill for a project this size. Keeping it simple makes the backend decisions the focus.

## 013 — Abandoned: yt-dlp server-side stream extraction
**Decision:** Abandoned in favor of YouTube IFrame API (see Decision 001 and 006)
**Why it failed:** YouTube's n-challenge and PO token requirements on EC2 IPs made reliable stream extraction for all videos impractical. bgutil provided PO tokens but n-challenge solving required Node.js + yt-dlp-ejs, and the resulting Docker image was too large for the EC2 disk. Full history preserved on the `ytdlp-playback` branch.

## 012 — nginx as reverse proxy, port 8000 not exposed publicly
**Decision:** nginx listens on 80/443 and proxies to uvicorn on port 8000; port 8000 is not open in the security group
**Alternatives considered:** Exposing port 8000 directly
**Why:** nginx handles TLS termination via Certbot, WebSocket upgrades cleanly, and is the standard approach. Keeps the app process off a privileged port and makes HTTPS straightforward.

## 011 — Docker + GitHub Actions for deployment
**Decision:** Containerize with Docker, deploy via GitHub Actions to EC2
**Alternatives considered:** Manual EC2 setup, bare uvicorn with systemd
**Why:** Keeps EC2 thin — just Docker, no manual dependency management. Redeployment is a single git push. Image is pinned and reproducible.

## 010 — Background music removed
**Decision:** Background music feature removed along with yt-dlp
**Why:** Background music depended on yt-dlp stream extraction, which was abandoned. The feature can be revisited independently if needed.

## 009 — Test dependencies in requirements-dev.txt
**Decision:** `pytest` and `httpx` live in `requirements-dev.txt`, which includes prod deps via `-r requirements.txt`
**Alternatives considered:** Single `requirements.txt` with all deps
**Why:** Keeps the production install lean — no test tooling needed at runtime.

## 008 — QR code generated client-side via qrcodejs
**Decision:** Generate QR code in the browser using the `qrcodejs` CDN library
**Alternatives considered:** Server-side generation with `qrcode[pil]` or `segno`
**Why:** The guest URL depends on the host's hostname, which the server doesn't know reliably. The browser does — so client-side generation means the QR code always points to the correct address without configuration. No Python dependencies added.

## 007 — WebSocket broadcasts full queue on every change
**Decision:** Send the full queue JSON to all clients on every add or remove
**Alternatives considered:** Diff/event-based messages
**Why:** Simpler to reason about at this scale — no client-side state reconciliation needed.

## 006 — Host Playback via YouTube IFrame API
**Decision:** Host page embeds a YouTube IFrame player; auto-advance is handled via `onStateChange` (fires when `YT.PlayerState.ENDED`)
**Alternatives considered:** yt-dlp stream extraction into a native `<video>` tag (see `ytdlp-playback` branch)
**Why:** The IFrame API handles all YouTube playback reliably without server-side infrastructure. `onStateChange` gives clean end-of-video detection for auto-advance. Video ID is extracted client-side from the submitted URL.
