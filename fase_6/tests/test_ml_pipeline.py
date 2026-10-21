import pytest
import numpy as np
from src.ml.train import run_training_pipeline, split_data, FEATURE_COLUMNS
from src.ml.evaluate import compute_classification_metrics
from data.generate_dataset import generate_synthetic_data
from src.ml.predictor import CardiacRiskPredictor, calculate_base_risk_score


@pytest.mark.unit
def test_compute_classification_metrics():
    """Testa o cálculo das métricas com previsões simuladas."""
    y_true = np.array([0, 1, 0, 1, 1])
    y_pred = np.array([0, 1, 0, 1, 0])
    y_proba = np.array([0.1, 0.9, 0.2, 0.8, 0.4])
    
    metrics = compute_classification_metrics(y_true, y_pred, y_proba)
    assert "accuracy" in metrics
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1_score" in metrics
    assert "roc_auc" in metrics
    assert "confusion_matrix" in metrics
    assert metrics["accuracy"] == 0.8


@pytest.mark.unit
def test_calculate_base_risk_score(task_patient_dict):
    """Valida o cálculo do score de risco base para o caso oficial."""
    score = calculate_base_risk_score(task_patient_dict)
    # No caso de teste, todas as 6 condições de risco são satisfeitas
    assert score == 6


@pytest.mark.integration
def test_predictor_inference(predictor, task_patient_data):
    """Valida a inferência do preditor com o modelo serializado."""
    pred = predictor.predict(task_patient_data)
    assert 0.0 <= pred.probabilidade_risco <= 1.0
    assert pred.pico_risco in (0, 1)
    assert pred.classificacao_texto in ("ALTO RISCO", "RISCO MODERADO", "BAIXO RISCO")
    # Para o caso crítico da task, deve ser classificado como pico de risco
    assert pred.pico_risco == 1
    assert pred.classificacao_texto == "ALTO RISCO"
