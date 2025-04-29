from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["qa"])
async def qa_root():
    """
    Stub endpoint for QA functionality.
    """
    return {"message": "QA endpoint placeholder"}
