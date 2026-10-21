from typing import Dict, Any
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


def compute_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray) -> Dict[str, Any]:
    """
    Calcula o conjunto completo de métricas de avaliação de classificação supervisionada.
    
    Args:
        y_true: Rótulos reais binários.
        y_pred: Predições de classe binária.
        y_proba: Probabilidades previstas da classe positiva (1).
        
    Returns:
        Dicionário com acurácia, precisão, recall, f1, roc_auc e matriz de confusão.
    """
    cm = confusion_matrix(y_true, y_pred)
    
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "confusion_matrix": cm.tolist(),
        "classification_report": classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    }
    return metrics
