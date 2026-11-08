"""Treina o modelo preditivo da Fase 6 durante o build (Render/CI).

Uso (na raiz do repositório):  python backend/bootstrap_model.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cardioia import paths  # noqa: E402,F401 - registra fase_6/ no sys.path
from src.config import MODEL_PIPELINE_PATH  # noqa: E402
from src.ml.train import run_training_pipeline  # noqa: E402

if __name__ == "__main__":
    if MODEL_PIPELINE_PATH.exists() and "--force" not in sys.argv:
        print(f"Modelo já existe em {MODEL_PIPELINE_PATH}")
    else:
        run_training_pipeline()
