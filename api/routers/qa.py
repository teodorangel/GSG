from fastapi import APIRouter
from api.models import QARequest, QAResponse

router = APIRouter()

@router.post("/", response_model=QAResponse)
async def run_query(req: QARequest) -> QAResponse:
    """
    Perform a RetrievalQA on the knowledge base (stubbed).

    Args:
        req (QARequest): The QA request containing query and optional product_id.

    Returns:
        QAResponse: Mocked answer and sources list.
    """
    # TODO: call actual agent
    answer = "Test answer"
    sources = ["src1", "src2"]
    return QAResponse(answer=answer, sources=sources)
