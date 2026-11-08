"""Resolução de caminhos e registro dos módulos das fases anteriores no sys.path.

O backend reaproveita, sem duplicar código:
  - fase_6/  -> pacote `src` (ML preditivo + pipeline multiagente + protocolos)
  - api/     -> pacote `chatbot` (IBM Watson Assistant + motor local da Fase 5)
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
FASE6_DIR = REPO_ROOT / "fase_6"
FASE5_API_DIR = REPO_ROOT / "api"


def register_legacy_modules() -> None:
    """Adiciona as pastas das fases anteriores ao sys.path (idempotente)."""
    for path in (FASE6_DIR, FASE5_API_DIR):
        p = str(path)
        if path.exists() and p not in sys.path:
            sys.path.append(p)


register_legacy_modules()
