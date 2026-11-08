import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from cardioia.config import settings  # noqa: E402
from cardioia.main import app  # noqa: E402
from cardioia.store import store  # noqa: E402


@pytest.fixture()
def client():
    store.clear()
    with TestClient(app) as c:
        yield c


def _token(client, user="medico"):
    pwd = settings.medico_password if user == "medico" else settings.paciente_password
    r = client.post("/api/auth/login", json={"username": user, "password": pwd})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


DEVICE = {"X-Device-Token": settings.device_token}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_login_invalid(client):
    r = client.post("/api/auth/login", json={"username": "medico", "password": "errada"})
    assert r.status_code == 401


def test_dashboard_requires_auth(client):
    assert client.get("/api/dashboard").status_code == 401


def test_telemetry_requires_device_token(client):
    body = {"bpm": 80, "spo2": 98, "temperature": 36.5, "systolic": 120}
    assert client.post("/api/telemetry", json=body).status_code == 401


def test_end_to_end_normal_reading(client):
    body = {"bpm": 75, "spo2": 98, "temperature": 36.5, "systolic": 118}
    r = client.post("/api/telemetry", json=body, headers=DEVICE)
    assert r.status_code == 200
    assert r.json()["ok"] is True

    dash = client.get("/api/dashboard", headers=_token(client)).json()
    assert dash["latest"]["bpm"] == 75
    assert dash["device"]["online"] is True
    assert dash["analysis"]["status_sinais"] == "NORMAL"
    assert len(dash["history"]) == 1


def test_critical_reading_generates_alert(client):
    body = {"bpm": 140, "spo2": 85, "temperature": 39.4, "systolic": 190}
    r = client.post("/api/telemetry", json=body, headers=DEVICE)
    assert r.json()["nivel"] == "CRITICO"

    headers = _token(client)
    dash = client.get("/api/dashboard", headers=headers).json()
    assert dash["analysis"]["nivel"] == "CRITICO"
    assert len(dash["analysis"]["alertas"]) == 4
    assert dash["alerts"][0]["nivel"] == "CRITICO"


def test_patient_view_is_simplified(client):
    client.post("/api/telemetry", json={"bpm": 80, "spo2": 97, "temperature": 36.8, "systolic": 125}, headers=DEVICE)
    dash = client.get("/api/dashboard", headers=_token(client, "paciente")).json()
    assert set(dash["analysis"].keys()) == {"nivel", "status_por_sinal", "mensagem_paciente"}
    assert "alerts" not in dash
    assert client.get("/api/alerts", headers=_token(client, "paciente")).status_code == 403


def test_simulate_and_chat(client):
    headers = _token(client)
    r = client.post("/api/simulate", json={"scenario": "critico"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["analysis"]["nivel"] == "CRITICO"

    sid = client.post("/api/chat/session", headers=headers).json()["session_id"]
    r = client.post("/api/chat", json={"message": "como estou? meus sinais", "session_id": sid}, headers=headers)
    assert r.status_code == 200
    assert "response" in r.json()
