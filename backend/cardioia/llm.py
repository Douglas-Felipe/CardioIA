"""Cliente LLM opcional (Gemini ou OpenAI) para reescrever a recomendação clínica.

Se nenhuma chave estiver configurada ou a chamada falhar, retorna None e o backend
usa o texto determinístico do pipeline multiagente da Fase 6 (fallback).
"""

import logging
from typing import Optional

import httpx

from .config import settings

logger = logging.getLogger("cardioia.llm")

SYSTEM_PROMPT = (
    "Você é o assistente clínico da plataforma CardioIA. Reescreva, em português do Brasil, "
    "a análise abaixo em no máximo 4 frases objetivas para a equipe médica, citando os sinais "
    "alterados, o nível de risco e as condutas prioritárias. Não invente dados nem diagnósticos; "
    "lembre que a decisão final é do médico."
)


def provider_name() -> str:
    if settings.gemini_api_key:
        return f"gemini:{settings.gemini_model}"
    if settings.openai_api_key:
        return f"openai:{settings.openai_model}"
    return "none"


def _call_gemini(prompt: str) -> Optional[str]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
    body = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 300},
    }
    r = httpx.post(url, params={"key": settings.gemini_api_key}, json=body, timeout=settings.llm_timeout_seconds)
    r.raise_for_status()
    parts = r.json()["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts).strip() or None


def _call_openai(prompt: str) -> Optional[str]:
    r = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.openai_api_key}"},
        json={
            "model": settings.openai_model,
            "temperature": 0.2,
            "max_tokens": 300,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=settings.llm_timeout_seconds,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip() or None


def summarize(prompt: str) -> Optional[str]:
    """Gera o resumo via LLM configurado; retorna None em caso de ausência/erro."""
    try:
        if settings.gemini_api_key:
            return _call_gemini(prompt)
        if settings.openai_api_key:
            return _call_openai(prompt)
    except Exception as exc:  # noqa: BLE001 - qualquer falha cai no fallback
        logger.warning("Falha na chamada ao LLM (%s): %s", provider_name(), exc)
    return None
