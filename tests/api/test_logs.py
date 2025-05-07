import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from api.main import create_app
from api.models import LogMessage

# Stub log_stream to yield predictable messages
def fake_log_stream(job_id: str):
    async def _gen():
        yield LogMessage(job_id=job_id, url="", status="started", detail=None, timestamp=datetime.utcnow())
        yield LogMessage(job_id=job_id, url="http://example.com", status="fetched", detail="{}", timestamp=datetime.utcnow())
        yield LogMessage(job_id=job_id, url="http://example.com/doc.pdf", status="ingested", detail=None, timestamp=datetime.utcnow())
        yield LogMessage(job_id=job_id, url="", status="completed", detail=None, timestamp=datetime.utcnow())
    return _gen()

@pytest.fixture(autouse=True)
def patch_log_stream(monkeypatch):
    # Monkey-patch the log_stream generator in the logs router
    import api.routers.logs as logs_module
    monkeypatch.setattr(logs_module, "log_stream", fake_log_stream)
    return None

def test_websocket_logs_sequence():
    app = create_app()
    client = TestClient(app)
    job_id = "testjob123"
    with client.websocket_connect(f"/logs/ws/{job_id}/") as ws:
        # Started
        msg1 = ws.receive_json()
        assert msg1["status"] == "started"
        # Fetched
        msg2 = ws.receive_json()
        assert msg2["status"] == "fetched"
        assert msg2["url"] == "http://example.com"
        # Ingested
        msg3 = ws.receive_json()
        assert msg3["status"] == "ingested"
        # Completed
        msg4 = ws.receive_json()
        assert msg4["status"] == "completed"
        # No more messages
        with pytest.raises(Exception):
            ws.receive_json(timeout=1) 