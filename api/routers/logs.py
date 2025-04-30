from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.models import LogMessage
from typing import AsyncGenerator
import asyncio
from fastapi.encoders import jsonable_encoder

router = APIRouter()

async def log_stream(job_id: str) -> AsyncGenerator[LogMessage, None]:
    """
    Launch the Scrapy 'seed' spider and stream its DataItems as LogMessages.
    """
    import sys
    import json
    from datetime import datetime

    # Notify client that crawling has started
    yield LogMessage(job_id=job_id, url="", status="started", detail=None, timestamp=datetime.utcnow())

    # Start Scrapy as a subprocess, outputting JSON items to stdout
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "scrapy", "crawl", "seed", "-o", "-", "--nolog",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Stream JSON lines and convert to LogMessage
    assert proc.stdout
    async for raw_line in proc.stdout:
        line = raw_line.decode().strip()
        try:
            data_item = json.loads(line)
        except json.JSONDecodeError:
            continue
        detail = data_item.get("payload")
        yield LogMessage(
            job_id=job_id,
            url=data_item.get("url", ""),
            status="fetched",
            detail=str(detail),
            timestamp=datetime.utcnow()
        )

    # Wait for crawler to finish and signal completion
    await proc.wait()
    yield LogMessage(job_id=job_id, url="", status="completed", detail=None, timestamp=datetime.utcnow())

@router.websocket("/ws/{job_id}")
@router.websocket("/ws/{job_id}/")
async def websocket_logs(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint streaming LogMessage JSON frames.
    """
    print(f"[logs router] Received WS connection request for job_id={job_id}")
    await websocket.accept()
    print(f"[logs router] WebSocket accepted for job_id={job_id}")
    try:
        async for msg in log_stream(job_id):
            print(f"[logs router] Sending log: {msg}")
            await websocket.send_json(jsonable_encoder(msg))
    except WebSocketDisconnect:
        pass
