from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.models import LogMessage
from typing import AsyncGenerator
import asyncio

router = APIRouter()

async def log_stream(job_id: str) -> AsyncGenerator[LogMessage, None]:
    """
    Stub generator: replace with real log fetch from crawler.
    """
    for i in range(3):
        await asyncio.sleep(0.1)
        yield LogMessage(
            job_id=job_id,
            url=f"https://example.com/page{i}",
            status="fetched",
            detail=None,
            timestamp=asyncio.get_event_loop().time()
        )

@router.websocket("/ws/{job_id}")
async def websocket_logs(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint streaming LogMessage JSON frames.
    """
    await websocket.accept()
    try:
        async for msg in log_stream(job_id):
            await websocket.send_json(msg.dict())
    except WebSocketDisconnect:
        pass
