import importlib
from fastapi.testclient import TestClient

app = importlib.import_module("app.payment-service.main").app

def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
