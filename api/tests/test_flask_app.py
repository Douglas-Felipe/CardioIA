import pytest
from app import create_app


@pytest.fixture
def test_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_route(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"CardioIA Assistant" in response.data


def test_health_route(test_client):
    response = test_client.get("/api/health")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
    assert "watson_connected" in json_data


def test_session_route(test_client):
    response = test_client.post("/api/session")
    assert response.status_code == 201
    json_data = response.get_json()
    assert "session_id" in json_data
    assert len(json_data["session_id"]) > 0


def test_chat_route_valid_message(test_client):
    payload = {"message": "Olá, gostaria de saber sobre prevenção"}
    response = test_client.post("/api/chat", json=payload)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "response" in json_data
    assert "intent" in json_data
    assert "risk_level" in json_data


def test_chat_route_empty_message(test_client):
    response = test_client.post("/api/chat", json={"message": "   "})
    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data


def test_triage_route(test_client):
    payload = {"text": "Sinto dor no peito e cansaço ao respirar"}
    response = test_client.post("/api/triage", json=payload)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "triagem_chatbot" in json_data
    assert "sugestao_ontologia" in json_data
