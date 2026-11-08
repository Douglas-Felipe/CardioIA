"""Contratos (Pydantic) da API do Backend Integrador."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

Role = Literal["medico", "paciente"]


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class UserOut(BaseModel):
    username: str
    name: str
    role: Role


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class TelemetryIn(BaseModel):
    """Payload enviado pelo dispositivo MicroPython (ESP32 no Wokwi)."""

    device_id: str = Field("cardioia-esp32-01", max_length=64)
    bpm: float = Field(..., ge=20, le=250, description="Frequência cardíaca (bpm)")
    spo2: float = Field(..., ge=50, le=100, description="Saturação de O2 (%)")
    temperature: float = Field(..., ge=25, le=45, description="Temperatura corporal (°C)")
    systolic: float = Field(..., ge=40, le=260, description="Pressão arterial sistólica (mmHg)")
    humidity: Optional[float] = Field(None, ge=0, le=100)
    edge_status: Optional[str] = Field(None, description="Classificação local feita no dispositivo")
    edge_alerts: List[str] = Field(default_factory=list)
    uptime_s: Optional[int] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None


class SimulateRequest(BaseModel):
    scenario: Literal["normal", "atencao", "critico"] = "normal"
