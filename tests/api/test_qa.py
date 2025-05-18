from fastapi.testclient import TestClient
from unittest.mock import patch
from api.main import create_app
from api.models import QARequest, QAResponse

client = TestClient(create_app())

@patch("api.routers.qa.run_query")  # monkeypatch the actual function
def test_run_query(mock_run_query):
    """
    Test the QA endpoint returns mocked answer and sources.
    """
    mock_run_query.return_value = QAResponse(answer="Test answer", sources=["src1", "src2"])
    req = QARequest(query="hello", product_id=1)
    response = client.post("/qa/", json=req.dict())
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Test answer"
    assert data["sources"] == ["src1", "src2"]
