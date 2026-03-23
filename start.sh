#!/bin/bash
set -e

# Start the bgutil PO token server in the background
npx --yes bgutil-ytdlp-pot-provider serve &

# Wait for it to be ready
sleep 3

# Start the app
exec uvicorn main:app --host 0.0.0.0 --port 8000
