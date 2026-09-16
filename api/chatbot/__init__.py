"""
Módulo do Assistente Conversacional CardioIA (IBM Watson Assistant + Local Engine)
"""

from .watson_client import WatsonAssistantClient
from .local_assistant_engine import LocalAssistantEngine

__all__ = ["WatsonAssistantClient", "LocalAssistantEngine"]
