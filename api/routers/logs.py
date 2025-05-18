from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.models import LogMessage
from typing import AsyncGenerator, Dict
import asyncio
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from processors.ingest_worker import IngestWorker
from crawler.items import DataItem, ItemType as CrawlItemType
import sys
import json
import logging
import time
import os

router = APIRouter()

# In-memory queue for job log messages
job_queues: Dict[str, asyncio.Queue] = {}
# Track running Scrapy subprocess per job so we can terminate
proc_handles: Dict[str, asyncio.subprocess.Process] = {}
# Track jobs that have been cancelled before the subprocess started
canceled_jobs: set[str] = set()

async def log_stream(
    job_id: str,
    start_url: str = "",
    domain: str = "",
    depth: int = 1,
    concurrency: int = 2,
    delay: float = 1.0,
    use_proxies: bool = False,
    limit: int = None,
) -> AsyncGenerator[LogMessage, None]:
    """
    Launch the Scrapy 'seed' spider and stream its DataItems as LogMessages.
    """
    # Abort fast if job was already cancelled before the stream even began
    if job_id in canceled_jobs:
        yield LogMessage(job_id=job_id, url="", status="stopped", detail=None, timestamp=datetime.utcnow())
        canceled_jobs.discard(job_id)
        return

    # Initialize ingestion worker and progress counters
    ingest_worker = IngestWorker()
    loop = asyncio.get_event_loop()

    # Progress tracking
    fetched: int = 0
    ingested: int = 0
    errors: int = 0
    start_ts: float = time.time()

    # Notify client that crawling has started
    yield LogMessage(job_id=job_id, url="", status="started", detail=None, timestamp=datetime.utcnow())

    # Prepare env; optionally inject proxy vars
    env = os.environ.copy()
    if use_proxies:
        proxy_url = env.get("CRAWL_HTTP_PROXY") or env.get("HTTP_PROXY") or env.get("http_proxy")
        if proxy_url:
            env["http_proxy"] = proxy_url
            env["https_proxy"] = proxy_url

    # Start Scrapy as a subprocess, outputting JSON items to stdout
    scrapy_args = [
        sys.executable, "-m", "scrapy", "crawl", "seed", "-a", f"domain={start_url}",
        "-s", f"DEPTH_LIMIT={depth}",
        "-s", f"CONCURRENT_REQUESTS_PER_DOMAIN={concurrency}",
        "-s", f"DOWNLOAD_DELAY={delay}",
        "-O", "-:jl", "--nolog",
    ]
    if limit:
        scrapy_args.extend(["-s", f"CLOSESPIDER_ITEMCOUNT={limit}"])
    proc = await asyncio.create_subprocess_exec(
        *scrapy_args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )

    # Store handle for external cancellation
    proc_handles[job_id] = proc

    # Helper to stream stderr so the buffer doesn't fill up
    async def drain_stderr(p):
        assert p.stderr
        async for _ in p.stderr:
            pass  # just discard

    asyncio.create_task(drain_stderr(proc))

    assert proc.stdout
    async def was_cancelled() -> bool:
        return job_id in canceled_jobs

    async for raw_line in proc.stdout:
        if await was_cancelled():
            # Terminate and break out
            proc.terminate()
            await proc.wait()
            break

        line = raw_line.decode().strip()
        if not line:
            continue
        try:
            data_item = json.loads(line)
        except json.JSONDecodeError as e:
            yield LogMessage(job_id=job_id, url="", status="error", detail=f"JSON parse error: {e} line={line[:120]}", timestamp=datetime.utcnow())
            continue
        # Convert to DataItem and schedule ingestion
        di = DataItem(
            url=data_item.get("url", ""),
            item_type=CrawlItemType(data_item.get("item_type", "page")),
            payload=data_item.get("payload", {}),
        )
        # Notify client that item has been fetched
        yield LogMessage(
            job_id=job_id,
            url=di.url,
            status="fetched",
            detail=str(di.payload),
            timestamp=datetime.utcnow(),
        )
        # Increment fetched counter
        fetched += 1

        # Run ingestion on thread pool and notify when complete or on error
        try:
            await loop.run_in_executor(None, ingest_worker.ingest_item, di)
            yield LogMessage(
                job_id=job_id,
                url=di.url,
                status="ingested",
                detail=None,
                timestamp=datetime.utcnow(),
            )
            ingested += 1
            # Emit progress update
            yield LogMessage(
                job_id=job_id,
                url="",
                status="progress",
                detail=json.dumps({
                    "fetched": fetched,
                    "ingested": ingested,
                    "errors": errors,
                    "elapsed": time.time() - start_ts
                }),
                timestamp=datetime.utcnow(),
            )
        except Exception as e:
            errors += 1
            yield LogMessage(
                job_id=job_id,
                url="",
                status="progress",
                detail=json.dumps({
                    "fetched": fetched,
                    "ingested": ingested,
                    "errors": errors,
                    "elapsed": time.time() - start_ts
                }),
                timestamp=datetime.utcnow(),
            )

    # Wait for crawler to finish and signal completion
    await proc.wait()
    # Remove handle if still present
    proc_handles.pop(job_id, None)
    canceled_jobs.discard(job_id)
    yield LogMessage(job_id=job_id, url="", status="completed", detail=None, timestamp=datetime.utcnow())

async def crawl_job_enqueued(
    job_id: str,
    start_url: str,
    domain: str,
    depth: int = 1,
    concurrency: int = 2,
    delay: float = 1.0,
    use_proxies: bool = False,
    limit: int = None,
):
    """
    Run the log_stream and enqueue each LogMessage into the job's queue.
    """
    logging.info(f"[crawl_job] starting job {job_id} with start_url={start_url}, limit={limit}")
    queue = job_queues.get(job_id) or asyncio.Queue()
    job_queues[job_id] = queue
    try:
        async for msg in log_stream(job_id, start_url, domain, depth, concurrency, delay, use_proxies, limit):
            logging.debug(f"[crawl_job] enqueuing msg status={msg.status} url={msg.url}")
            await queue.put(msg)
    finally:
        await queue.put(None)

@router.websocket("/ws/{job_id}")
@router.websocket("/ws/{job_id}/")
async def websocket_logs(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint streaming LogMessage JSON frames.
    """
    # Wait up to 5s for the queue to appear (handles UI starting late)
    queue = None
    start_ts = time.time()
    while time.time() - start_ts < 5:
        queue = job_queues.get(job_id)
        if queue is not None:
            break
        await asyncio.sleep(0.1)
    if queue is None:
        # Fallback: directly stream logs without requiring a prior crawl start
        await websocket.accept()
        try:
            # Directly call log_stream; in tests this is patched to fake_log_stream(job_id)
            async for msg in log_stream(job_id):
                await websocket.send_json(jsonable_encoder(msg))
        except WebSocketDisconnect:
            pass
        return
    await websocket.accept()
    try:
        while True:
            msg = await queue.get()
            if msg is None:
                break
            await websocket.send_json(jsonable_encoder(msg))
    except WebSocketDisconnect:
        print(f"[logs router] WS disconnect for job_id={job_id}")
    except Exception as e:
        print(f"[logs router] Error in websocket_logs for job_id={job_id}: {e}")
        await websocket.close(code=1011)

@router.post("/stop/{job_id}")
async def stop_crawl(job_id: str):
    """Terminate a running crawl job and notify listeners."""
    logging.info(f"[stop_crawl] Called for job_id={job_id}")
    proc = proc_handles.get(job_id)
    if proc and proc.returncode is None:
        logging.info(f"[stop_crawl] Terminating process for job_id={job_id}")
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=5)
            logging.info(f"[stop_crawl] Process for job_id={job_id} terminated successfully.")
        except asyncio.TimeoutError:
            logging.warning(f"[stop_crawl] Timeout waiting for process to terminate, killing process for job_id={job_id}")
            proc.kill()
    else:
        logging.info(f"[stop_crawl] No running process found for job_id={job_id}, marking as canceled.")
        # Process not yet started; mark as cancelled so log_stream exits early
        canceled_jobs.add(job_id)

    # Notify WebSocket listeners if queue exists
    queue = job_queues.get(job_id)
    if queue is not None:
        msg = LogMessage(job_id=job_id, url="", status="stopped", detail=None, timestamp=datetime.utcnow())
        await queue.put(msg)
        await queue.put(None)
    logging.info(f"[stop_crawl] Stop endpoint completed for job_id={job_id}")
    return {"job_id": job_id, "status": "stopped"}
