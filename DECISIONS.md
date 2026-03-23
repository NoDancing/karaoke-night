# Technical Decisions

## 001 — YouTube Playback Method
**Decision:** yt-dlp + ffmpeg
**Alternatives considered:** YouTube iframe embed, youtube-dl
**Why:** iframe gives less programmatic control. yt-dlp allows us to serve both video streams for karaoke songs and audio-only streams for background music between singers — a feature the iframe approach can't support cleanly.

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

## 005 — Frontend
**Decision:** Vanilla HTML/JS
**Alternatives considered:** React, HTMX
**Why:** No build step, easy to read and modify. React is overkill for a project this size. Keeping it simple makes the backend decisions the focus.

## 006 — Host Playback via yt-dlp Stream Extraction
**Decision:** Backend extracts direct stream URL via yt-dlp; browser plays it in a native `<video>` tag
**Alternatives considered:** YouTube IFrame API
**Why:** Avoids any dependency on the YouTube IFrame API and keeps playback consistent with how background music will work in Step 7 (audio-only streams). Stream URLs are fetched fresh on each song start since they expire.
