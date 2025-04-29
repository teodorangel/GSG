from fastapi import APIRouter
from api.models import PlanRequest, PlanResponse
from api.agent import run_plan

router = APIRouter()

@router.post("/", response_model=PlanResponse)
async def create_plan(req: PlanRequest) -> PlanResponse:
    """
    Create a project plan based on selected products, budget, and site size.

    Args:
        req (PlanRequest): Contains product IDs, budget, and site size.

    Returns:
        PlanResponse: Step-by-step plan, bill of materials, and estimates.
    """
    return run_plan(req.product_ids, req.budget, req.site_size_sqft)
