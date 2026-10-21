import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env se existir
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Caminhos do projeto
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
SRC_DIR = BASE_DIR / "src"

DATASET_CSV_PATH = DATA_DIR / "dataset_simulado.csv"
MODEL_PIPELINE_PATH = MODELS_DIR / "cardiac_risk_pipeline.joblib"
METRICS_JSON_PATH = MODELS_DIR / "metrics_summary.json"

# Configurações do Mapika Decider
MAPIKA_MODEL_NAME = os.getenv("MAPIKA_MODEL_NAME", "decider-4b")

# Garantir existência de pastas
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
