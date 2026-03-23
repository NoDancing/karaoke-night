# CLAUDE.md

## Project
karaoke-night — a real-time karaoke queue app. Guests submit YouTube URLs from their phones. The host screen plays them in order. Background music fills the silence between singers.

## Rules for this project
- One feature at a time
- Before writing any code, tell me what files you plan to create/edit and what each one will do
- No large multi-file changes without discussion
- After each feature, we update README.md and DECISIONS.md before moving on

## Tech Stack
- Backend: FastAPI
- Playback: yt-dlp + ffmpeg
- State: in-memory Python list (no database)
- Frontend: Vanilla HTML/JS
- Real-time: WebSockets

## Build Order
1. Basic FastAPI server + queue API (add, list, remove)
2. Host playback page (plays YouTube video, auto-advances)
3. Guest submission page (URL + singer name → queue)
4. Real-time updates via WebSocket
5. Admin controls (skip, reorder, delete)
6. QR code display on host screen
7. Background music (audio-only, plays between songs)

## Current Status
- [x] README.md written
- [x] DECISIONS.md started
- [x] CLAUDE.md created
- [ ] Step 1: FastAPI server + queue API

## What's Next
Step 1. Basic FastAPI server with three endpoints:
- POST /queue — add a song
- GET /queue — list the queue
- DELETE /queue/{id} — remove a song

## Documentation Rules
- After every feature, update the Current Status in CLAUDE.md
- If a technical decision was made, add it to DECISIONS.md before moving on
- If the README needs updating, flag it and I will write it myself

## Hard Rules
- Never begin a new feature until the user explicitly says "README is updated" or "ready to continue"
