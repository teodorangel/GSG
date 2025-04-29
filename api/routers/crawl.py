from fastapi import APIRouter
from api.models import CrawlRequest, CrawlResponse
import uuid

router = APIRouter()

@router.post("/", response_model=CrawlResponse)
async def start_crawl(req: CrawlRequest) -> CrawlResponse:
    """
    Enqueue a new crawl job for the given domain and parameters.

    Args:
        req (CrawlRequest): Crawl options including domain, depth, concurrency, and delay.

    Returns:
        CrawlResponse: Contains a unique job ID and initial status.
    """
    job_id = str(uuid.uuid4())
    # TODO: integrate with crawler queue/service
    return CrawlResponse(job_id=job_id, status="created")
