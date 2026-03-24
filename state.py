from fastapi import WebSocket
from typing import List

queue: List[dict] = []
clients: set[WebSocket] = set()
event_title: str = "Karaoke Night"
