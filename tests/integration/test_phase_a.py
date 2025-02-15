from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_a2_formatting():
    response = client.post("/run?task=Format+/data/format.md+with+prettier@3.4.2")
    assert response.status_code == 200
    content = client.get("/read?path=/data/format.md").text
    assert "formatted content" in content
