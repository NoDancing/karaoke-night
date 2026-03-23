import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import main


@pytest.fixture(autouse=True)
def clear_queue():
    main.queue.clear()
    main.clients.clear()
    yield
    main.queue.clear()
    main.clients.clear()


client = TestClient(main.app)


# --- POST /queue ---

def test_add_song_returns_entry():
    res = client.post("/queue", json={"url": "https://youtube.com/watch?v=abc", "singer": "Alice"})
    assert res.status_code == 201
    data = res.json()
    assert data["singer"] == "Alice"
    assert data["url"] == "https://youtube.com/watch?v=abc"
    assert "id" in data
    assert "added_at" in data


def test_add_song_appears_in_queue():
    client.post("/queue", json={"url": "https://youtube.com/watch?v=abc", "singer": "Alice"})
    res = client.get("/queue")
    assert len(res.json()) == 1


def test_add_multiple_songs_preserves_order():
    client.post("/queue", json={"url": "https://youtube.com/watch?v=1", "singer": "Alice"})
    client.post("/queue", json={"url": "https://youtube.com/watch?v=2", "singer": "Bob"})
    queue = client.get("/queue").json()
    assert queue[0]["singer"] == "Alice"
    assert queue[1]["singer"] == "Bob"


# --- GET /queue ---

def test_get_queue_empty():
    res = client.get("/queue")
    assert res.status_code == 200
    assert res.json() == []


# --- DELETE /queue/{id} ---

def test_delete_song_removes_it():
    entry = client.post("/queue", json={"url": "https://youtube.com/watch?v=abc", "singer": "Alice"}).json()
    res = client.delete(f"/queue/{entry['id']}")
    assert res.status_code == 204
    assert client.get("/queue").json() == []


def test_delete_nonexistent_song_returns_404():
    res = client.delete("/queue/nonexistent-id")
    assert res.status_code == 404


def test_delete_removes_correct_song():
    a = client.post("/queue", json={"url": "https://youtube.com/watch?v=1", "singer": "Alice"}).json()
    b = client.post("/queue", json={"url": "https://youtube.com/watch?v=2", "singer": "Bob"}).json()
    client.delete(f"/queue/{a['id']}")
    queue = client.get("/queue").json()
    assert len(queue) == 1
    assert queue[0]["id"] == b["id"]


# --- PUT /queue/reorder ---

def test_reorder_queue():
    a = client.post("/queue", json={"url": "https://youtube.com/watch?v=1", "singer": "Alice"}).json()
    b = client.post("/queue", json={"url": "https://youtube.com/watch?v=2", "singer": "Bob"}).json()
    res = client.put("/queue/reorder", json={"ids": [b["id"], a["id"]]})
    assert res.status_code == 200
    queue = res.json()
    assert queue[0]["id"] == b["id"]
    assert queue[1]["id"] == a["id"]


def test_reorder_with_wrong_ids_returns_400():
    client.post("/queue", json={"url": "https://youtube.com/watch?v=1", "singer": "Alice"})
    res = client.put("/queue/reorder", json={"ids": ["wrong-id"]})
    assert res.status_code == 400


# --- GET /queue/current/stream ---

def test_stream_returns_url():
    client.post("/queue", json={"url": "https://youtube.com/watch?v=abc", "singer": "Alice"})
    mock_info = {"url": "https://stream.example.com/video.mp4", "title": "Test Song"}
    with patch("main.yt_dlp.YoutubeDL") as MockYDL:
        instance = MagicMock()
        instance.__enter__ = MagicMock(return_value=instance)
        instance.__exit__ = MagicMock(return_value=False)
        instance.extract_info.return_value = mock_info
        MockYDL.return_value = instance
        res = client.get("/queue/current/stream")
    assert res.status_code == 200
    assert res.json()["stream_url"] == "https://stream.example.com/video.mp4"


def test_stream_empty_queue_returns_404():
    res = client.get("/queue/current/stream")
    assert res.status_code == 404


# --- WebSocket /ws ---

def test_websocket_receives_queue_on_connect():
    client.post("/queue", json={"url": "https://youtube.com/watch?v=1", "singer": "Alice"})
    with client.websocket_connect("/ws") as ws:
        data = ws.receive_json()
        assert len(data) == 1
        assert data[0]["singer"] == "Alice"


def test_websocket_receives_broadcast_on_add():
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()  # initial state
        client.post("/queue", json={"url": "https://youtube.com/watch?v=1", "singer": "Bob"})
        data = ws.receive_json()
        assert len(data) == 1
        assert data[0]["singer"] == "Bob"


def test_websocket_receives_broadcast_on_delete():
    entry = client.post("/queue", json={"url": "https://youtube.com/watch?v=1", "singer": "Alice"}).json()
    with client.websocket_connect("/ws") as ws:
        ws.receive_json()  # initial state
        client.delete(f"/queue/{entry['id']}")
        data = ws.receive_json()
        assert data == []
