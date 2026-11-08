"""Configurações do Backend Integrador lidas de variáveis de ambiente."""

import os
from dataclasses import dataclass, field
from typing import Dict, List

from dotenv import load_dotenv

from .paths import BACKEND_DIR

load_dotenv(BACKEND_DIR / ".env")


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    # Segurança
    jwt_secret: str = os.getenv("JWT_SECRET", "cardioia-dev-secret-change-me")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "720"))
    device_token: str = os.getenv("DEVICE_TOKEN", "cardioia-device-demo-token")

    # Usuários de demonstração (perfil médico e perfil paciente)
    medico_user: str = os.getenv("MEDICO_USER", "medico")
    medico_password: str = os.getenv("MEDICO_PASSWORD", "cardio123")
    medico_name: str = os.getenv("MEDICO_NAME", "Dra. Ana Cardoso")
    paciente_user: str = os.getenv("PACIENTE_USER", "paciente")
    paciente_password: str = os.getenv("PACIENTE_PASSWORD", "cardio123")
    paciente_name: str = os.getenv("PACIENTE_NAME", "João da Silva")

    # CORS (lista separada por vírgula; "*" libera todas as origens)
    cors_origins: List[str] = field(
        default_factory=lambda: [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
    )

    # Telemetria
    history_size: int = int(os.getenv("HISTORY_SIZE", "500"))
    device_offline_seconds: int = int(os.getenv("DEVICE_OFFLINE_SECONDS", "30"))

    # LLM opcional (reescrita da recomendação em linguagem natural)
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm_timeout_seconds: float = _env_float("LLM_TIMEOUT_SECONDS", 8.0)

    # Features operacionais FIXAS do modelo da Fase 6
    # (os sensores fornecem FC, SpO2, temperatura e PA sistólica)
    fixed_features: Dict[str, float] = field(
        default_factory=lambda: {
            "idade_media": _env_float("FEATURE_IDADE", 62.0),
            "carga_sistema": _env_float("FEATURE_CARGA_SISTEMA", 82.0),
            "tempo_espera": _env_float("FEATURE_TEMPO_ESPERA", 35.0),
            "densidade_eventos": _env_float("FEATURE_DENSIDADE_EVENTOS", 3.0),
            "eventos_24h": _env_float("FEATURE_EVENTOS_24H", 2.0),
            "disponibilidade_recursos": _env_float("FEATURE_DISPONIBILIDADE_RECURSOS", 65.0),
        }
    )


settings = Settings()
