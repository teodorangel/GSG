from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["crawl"])
async def crawl_root():
    """
    Stub endpoint for crawl functionality.
    """
    return {"message": "Crawl endpoint placeholder"}
