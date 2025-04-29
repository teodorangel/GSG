from fastapi import FastAPI
from api.routers.products import router as products_router
from api.routers.crawl import router as crawl_router
from api.routers.qa import router as qa_router
from api.routers.logs import router as logs_router

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI app with routers registered.
    """
    app = FastAPI(title="GrandGuruAI API")
    app.include_router(products_router, prefix="/products", tags=["products"])
    app.include_router(crawl_router, prefix="/crawl", tags=["crawl"])
    app.include_router(qa_router, prefix="/qa", tags=["qa"])
    app.include_router(logs_router, prefix="/logs", tags=["logs"])
    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
