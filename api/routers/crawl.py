from fastapi import APIRouter, BackgroundTasks
from api.models import CrawlRequest, CrawlResponse
import uuid
from api.routers.logs import crawl_job_enqueued, job_queues
import logging
import asyncio

router = APIRouter()

@router.post("/", response_model=CrawlResponse)
async def start_crawl(req: CrawlRequest, background_tasks: BackgroundTasks) -> CrawlResponse:
    """
    Enqueue a new crawl job for the given domain and parameters.

    Args:
        req (CrawlRequest): Crawl options including domain, depth, concurrency, and delay.
        background_tasks (BackgroundTasks): FastAPI background tasks

    Returns:
        CrawlResponse: Contains a unique job ID and initial status.
    """
    job_id = str(uuid.uuid4())
    # Initialize in-memory queue so WS can connect immediately
    queue = asyncio.Queue()
    job_queues[job_id] = queue
    logging.info(
        f"[crawl] scheduling job {job_id} for {req.domain}, depth={req.depth}, concurrency={req.concurrency}, delay={req.delay}, use_proxies={req.use_proxies}"
    )
    # Schedule the crawl and ingestion in the background, passing domain
    background_tasks.add_task(
        crawl_job_enqueued,
        job_id,
        req.domain,
        req.domain,
        req.depth or 1,
        req.concurrency or 2,
        req.delay or 1.0,
        req.use_proxies or False,
    )
    return CrawlResponse(job_id=job_id, status="created")
