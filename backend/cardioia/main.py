"""CardioIA - Backend Integrador (FastAPI).

Executar localmente (na raiz do repositório):
    uvicorn cardioia.main:app --reload --app-dir backend
"""

import logging
import random
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from . import __version__, llm
from .ai_engine import get_engine
from .auth import authenticate, create_access_token, get_current_user, require_medico, verify_device
from .chat_service import get_chat
from .config import settings
from .schemas import ChatRequest, LoginRequest, LoginResponse, SimulateRequest, TelemetryIn, UserOut
from .store import store

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("cardioia.api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Pré-carrega os motores de IA (ML da Fase 6 e chatbot da Fase 5)
    get_engine()
    get_chat()
    yield


app = FastAPI(
    title="CardioIA - Backend Integrador",
    version=__version__,
    description="Sensor → MicroPython → Backend Python → APIs de IA → UI (Web/Mobile)",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _ingest(reading: Dict[str, Any]) -> Dict[str, Any]:
    analysis = get_engine().analyze(reading["bpm"], reading["spo2"], reading["temperature"], reading["systolic"])
    return store.add(reading, analysis)


# ---------------------------------------------------------------- públicos
@app.get("/")
def root():
    return {"service": "CardioIA Backend Integrador", "version": __version__, "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    engine = get_engine()
    return {
        "status": "ok",
        "ml_fase6": engine.ml_available,
        "ml_error": engine.ml_error,
        "chat_engine": get_chat().engine,
        "llm_provider": llm.provider_name(),
        "readings": store.total_received,
        "device_online": store.device_online(),
    }


@app.post("/api/auth/login", response_model=LoginResponse)
def login(body: LoginRequest):
    user = authenticate(body.username, body.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário ou senha inválidos")
    return LoginResponse(access_token=create_access_token(user), user=user)


@app.get("/api/auth/me", response_model=UserOut)
def me(user: UserOut = Depends(get_current_user)):
    return user


# --------------------------------------------------------------- IoT (edge)
@app.post("/api/telemetry", dependencies=[Depends(verify_device)])
def telemetry(body: TelemetryIn):
    """Recebe os sinais do ESP32 (MicroPython) e devolve o veredito da IA para o display OLED."""
    reading = body.model_dump()
    reading["source"] = "device"
    entry = _ingest(reading)
    a = entry["analysis"]
    ml = a.get("ml") or {}
    return {
        "ok": True,
        "nivel": a["nivel"],
        "classificacao_ml": ml.get("classificacao", "N/D"),
        "probabilidade": ml.get("probabilidade"),
        "alertas": len(a["alertas"]),
    }


# ----------------------------------------------------------- autenticados
def _public_latest(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {k: entry.get(k) for k in ("ts", "bpm", "spo2", "temperature", "systolic", "humidity", "source", "device_id", "edge_status")}


@app.get("/api/dashboard")
def dashboard(user: UserOut = Depends(get_current_user), limit: int = Query(60, ge=1, le=500)):
    """Endpoint único consumido pelo Web e pelo Mobile (polling)."""
    latest = store.latest()
    payload: Dict[str, Any] = {
        "user": user.model_dump(),
        "server_time": time.time(),
        "device": {
            "online": store.device_online(),
            "last_seen": latest["ts"] if latest else None,
            "total_readings": store.total_received,
        },
        "latest": _public_latest(latest) if latest else None,
        "history": store.history(limit),
    }
    if latest is None:
        payload["analysis"] = None
    elif user.role == "medico":
        payload["analysis"] = latest["analysis"]
        payload["alerts"] = store.alerts()
    else:
        a = latest["analysis"]
        payload["analysis"] = {
            "nivel": a["nivel"],
            "status_por_sinal": a["status_por_sinal"],
            "mensagem_paciente": a["mensagem_paciente"],
        }
    return payload


@app.get("/api/vitals/latest")
def vitals_latest(user: UserOut = Depends(get_current_user)):
    latest = store.latest()
    if not latest:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nenhuma leitura recebida ainda")
    return latest if user.role == "medico" else _public_latest(latest)


@app.get("/api/vitals/history")
def vitals_history(limit: int = Query(60, ge=1, le=500), _: UserOut = Depends(get_current_user)):
    return store.history(limit)


@app.get("/api/alerts")
def alerts(_: UserOut = Depends(require_medico)):
    return store.alerts()


_SCENARIOS = {
    "normal": {"bpm": (68, 88), "spo2": (96, 99), "temperature": (36.2, 37.0), "systolic": (110, 130)},
    "atencao": {"bpm": (101, 115), "spo2": (92, 94), "temperature": (37.6, 38.3), "systolic": (142, 165)},
    "critico": {"bpm": (125, 150), "spo2": (82, 89), "temperature": (39.0, 39.8), "systolic": (182, 200)},
}


@app.post("/api/simulate")
def simulate(body: SimulateRequest, _: UserOut = Depends(require_medico)):
    """Gera uma leitura sintética (útil quando o Wokwi não está em execução)."""
    ranges = _SCENARIOS[body.scenario]
    reading = {k: round(random.uniform(*v), 1) for k, v in ranges.items()}
    reading.update({"device_id": "simulador-web", "source": "simulador", "humidity": None, "edge_status": None, "edge_alerts": []})
    entry = _ingest(reading)
    return {"latest": _public_latest(entry), "analysis": entry["analysis"]}


@app.delete("/api/vitals")
def clear_vitals(_: UserOut = Depends(require_medico)):
    store.clear()
    return {"ok": True}


@app.post("/api/chat/session")
def chat_session(_: UserOut = Depends(get_current_user)):
    return {"session_id": get_chat().create_session(), "engine": get_chat().engine}


@app.post("/api/chat")
def chat(body: ChatRequest, _: UserOut = Depends(get_current_user)):
    return get_chat().send(body.message.strip(), body.session_id)
