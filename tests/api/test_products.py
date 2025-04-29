import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_list_products():
    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data and "total" in data
    assert isinstance(data["items"], list)
    assert data["total"] == 0

@pytest.mark.parametrize("product_id", [1, 42])
def test_get_product(product_id):
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["model"] == "MODEL123"
