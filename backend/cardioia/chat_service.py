"""Integração com o assistente conversacional da Fase 5 (IBM Watson + motor local).

Enriquece a resposta com o contexto em tempo real dos sinais vitais do paciente
quando o usuário pergunta sobre seu estado atual.
"""

import logging
import re
from typing import Any, Dict, Optional

from . import paths  # noqa: F401 - registra api/ no sys.path
from .store import store

logger = logging.getLogger("cardioia.chat")

_STATUS_PATTERN = re.compile(r"\b(meus? sinais|meu estado|como estou|status|sinais vitais|batimentos|satura[cç][aã]o)\b", re.I)


class ChatService:
    def __init__(self) -> None:
        self._client = None
        try:
            from chatbot.watson_client import WatsonAssistantClient  # api/chatbot (Fase 5)

            self._client = WatsonAssistantClient()
        except Exception as exc:  # noqa: BLE001
            logger.exception("Chatbot da Fase 5 indisponível: %s", exc)

    @property
    def engine(self) -> str:
        if self._client is None:
            return "indisponivel"
        return "ibm_watson_assistant_v2" if self._client.is_watson_available() else "local_resilient_engine"

    def create_session(self) -> Optional[str]:
        return self._client.create_session() if self._client else None

    def send(self, message: str, session_id: Optional[str]) -> Dict[str, Any]:
        if self._client is None:
            return {
                "response": "O assistente está temporariamente indisponível. Em caso de emergência, ligue 192.",
                "risk_level": "BAIXO_RISCO",
                "session_id": session_id,
                "engine": "indisponivel",
            }
        result = self._client.send_message(message, session_id=session_id)

        if _STATUS_PATTERN.search(message):
            latest = store.latest()
            if latest:
                a = latest["analysis"]
                result["response"] += (
                    "\n\n**📡 Monitorização em tempo real (CardioIA IoT):**\n"
                    f"- FC: {latest['bpm']:.0f} bpm | SpO2: {latest['spo2']:.0f}% | "
                    f"Temp: {latest['temperature']:.1f} °C | PA sistólica: {latest['systolic']:.0f} mmHg\n"
                    f"- Situação: **{a['nivel']}** — {a['mensagem_paciente']}"
                )
                result["vitals_context"] = True
        return result


_chat: Optional[ChatService] = None


def get_chat() -> ChatService:
    global _chat
    if _chat is None:
        _chat = ChatService()
    return _chat
