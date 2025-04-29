from fastapi.testclient import TestClient
from api.main import create_app
from api.models import CrawlRequest, CrawlResponse

client = TestClient(create_app())

def test_start_crawl():
    req = CrawlRequest(domain="example.com", depth=2, concurrency=3, delay=0.5)
    response = client.post("/crawl/", json=req.dict())
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data and "status" in data
    assert data["status"] == "created"
