import httpx
# Monkey-patch httpx.Client.__init__ to ignore 'app' kwarg for TestClient compatibility
_orig_httpx_init = httpx.Client.__init__
def _patched_httpx_init(self, *args, **kwargs):
    kwargs.pop("app", None)
    return _orig_httpx_init(self, *args, **kwargs)
httpx.Client.__init__ = _patched_httpx_init
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers.products import router as products_router
from api.routers.crawl import router as crawl_router
from api.routers.qa import router as qa_router
from api.routers.logs import router as logs_router
from api.routers.plan import router as plan_router
from api.routers.admin import router as admin_router
# Monkey-patch FastAPI's TestClient to handle unexpected 'app' kwarg issues
from fastapi.testclient import TestClient as _FastAPITestClient
_orig_testclient_init = _FastAPITestClient.__init__
def _patched_testclient_init(self, *args, **kwargs):
    # Pop app kwarg if passed to httpx.Client
    kwargs.pop("app", None)
    try:
        return _orig_testclient_init(self, *args, **kwargs)
    except TypeError:
        # Fallback to positional init
        return _orig_testclient_init(self, *args)
_FastAPITestClient.__init__ = _patched_testclient_init
import fastapi
import uvicorn
from fastapi.staticfiles import StaticFiles

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI app with routers registered.
    """
    app = FastAPI(title="GrandGuruAI API")
    # Allow CORS from any origin (including WebSocket upgrades) for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(products_router, prefix="/products", tags=["products"])
    app.include_router(crawl_router, prefix="/crawl", tags=["crawl"])
    app.include_router(qa_router, prefix="/qa", tags=["qa"])
    app.include_router(logs_router, prefix="/logs", tags=["logs"])
    app.include_router(plan_router, prefix="/plan", tags=["plan"])
    app.include_router(admin_router)
    return app


app = create_app()

# Serve static files for images and documents
app.mount("/static/images", StaticFiles(directory="images"), name="images")
app.mount("/static/documents", StaticFiles(directory="documents"), name="documents")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
