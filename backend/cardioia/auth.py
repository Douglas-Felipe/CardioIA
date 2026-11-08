"""Autenticação JWT com usuários de demonstração (médico e paciente)."""

import hmac
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings
from .schemas import UserOut

_bearer = HTTPBearer(auto_error=False)


def _users() -> Dict[str, Dict[str, str]]:
    return {
        settings.medico_user: {
            "password": settings.medico_password,
            "name": settings.medico_name,
            "role": "medico",
        },
        settings.paciente_user: {
            "password": settings.paciente_password,
            "name": settings.paciente_name,
            "role": "paciente",
        },
    }


def authenticate(username: str, password: str) -> Optional[UserOut]:
    record = _users().get(username.strip().lower())
    if not record or not hmac.compare_digest(record["password"], password):
        return None
    return UserOut(username=username.strip().lower(), name=record["name"], role=record["role"])


def create_access_token(user: UserOut) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.username,
        "name": user.name,
        "role": user.role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> UserOut:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token ausente", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido ou expirado", headers={"WWW-Authenticate": "Bearer"})
    return UserOut(username=payload["sub"], name=payload.get("name", payload["sub"]), role=payload["role"])


def require_medico(user: UserOut = Depends(get_current_user)) -> UserOut:
    if user.role != "medico":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito ao perfil médico")
    return user


def verify_device(x_device_token: Optional[str] = Header(None)) -> None:
    """Valida o token simples enviado pelo dispositivo IoT no header X-Device-Token."""
    if not x_device_token or not hmac.compare_digest(x_device_token, settings.device_token):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Device token inválido")
