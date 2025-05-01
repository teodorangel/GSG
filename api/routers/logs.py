from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.models import LogMessage
from typing import AsyncGenerator
import asyncio
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from processors.ingest_worker import IngestWorker
from crawler.items import DataItem, ItemType as CrawlItemType

router = APIRouter()

async def log_stream(job_id: str) -> AsyncGenerator[LogMessage, None]:
    """
    Launch the Scrapy 'seed' spider and stream its DataItems as LogMessages.
    """
    import sys
    import json

    # Initialize ingestion worker
    ingest_worker = IngestWorker()
    loop = asyncio.get_event_loop()

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
        # Convert to DataItem and schedule ingestion
        di = DataItem(
            url=data_item.get("url", ""),
            item_type=CrawlItemType(data_item.get("item_type", "page")),
            payload=data_item.get("payload", {}),
        )
        # Run ingestion on thread pool
        await loop.run_in_executor(None, ingest_worker.ingest_item, di)
        # Stream the same info to client
        yield LogMessage(
            job_id=job_id,
            url=di.url,
            status="fetched",
            detail=str(di.payload),
            timestamp=datetime.utcnow(),
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
