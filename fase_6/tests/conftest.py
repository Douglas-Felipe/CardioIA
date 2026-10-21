import pytest
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path para importação de src e data
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.schemas import PatientData
from src.ml.predictor import CardiacRiskPredictor
from src.agents.runner import MultiAgentPipelineRunner


@pytest.fixture
def task_patient_dict():
    """Dicionário oficial com os dados do paciente de teste."""
    return {
        "idade_media": 62,
        "carga_sistema": 92,
        "tempo_espera": 75,
        "fc_media": 118,
        "spo2_media": 89,
        "pa_sistolica": 100,
        "temperatura": 37.5,
        "densidade_eventos": 7,
        "eventos_24h": 5,
        "disponibilidade recursos": 25
    }


@pytest.fixture
def task_patient_data(task_patient_dict):
    """Instância do schema PatientData."""
    return PatientData(**task_patient_dict)


@pytest.fixture
def predictor():
    """Instância do preditor de risco treinado."""
    return CardiacRiskPredictor()


@pytest.fixture
def runner():
    """Instância do runner multiagente com Mapika Decider."""
    return MultiAgentPipelineRunner()
