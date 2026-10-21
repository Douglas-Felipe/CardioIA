import json
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV
import joblib

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.config import DATASET_CSV_PATH, MODEL_PIPELINE_PATH, METRICS_JSON_PATH
from src.ml.evaluate import compute_classification_metrics
from data.generate_dataset import generate_synthetic_data

FEATURE_COLUMNS = [
    "idade_media",
    "carga_sistema",
    "tempo_espera",
    "fc_media",
    "spo2_media",
    "pa_sistolica",
    "temperatura",
    "densidade_eventos",
    "eventos_24h",
    "disponibilidade_recursos"
]
TARGET_COLUMN = "pico_risco"


def load_or_generate_data(csv_path: Path = DATASET_CSV_PATH) -> pd.DataFrame:
    """Carrega o dataset do disco ou gera caso ainda não exista."""
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return generate_synthetic_data(n=5000)


def split_data(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Separa variáveis explicativas e alvo com split estratificado."""
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)


def train_and_compare_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> Dict[str, Any]:
    """
    Treina e compara múltiplos algoritmos de classificação supervisionada:
    Random Forest, Gradient Boosting, Logistic Regression, KNN e SVM.
    """
    candidates = {
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "SVM": CalibratedClassifierCV(SVC(random_state=42), ensemble=False)
    }
    
    benchmark_results = {}
    best_name = None
    best_roc_auc = -1.0
    best_pipeline = None

    print("\n=== BENCHMARK DE MODELOS DE CLASSIFICAÇÃO ===")
    for name, estimator in candidates.items():
        # Pipeline com escalonador e classificador
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("classifier", estimator)
        ])
        
        # Cross-validation de 5 folds em treino
        cv_scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring="roc_auc")
        pipe.fit(X_train, y_train)
        
        y_pred = pipe.predict(X_test)
        y_proba = pipe.predict_proba(X_test)[:, 1]
        metrics = compute_classification_metrics(y_test, y_pred, y_proba)
        metrics["cv_roc_auc_mean"] = float(cv_scores.mean())
        metrics["cv_roc_auc_std"] = float(cv_scores.std())
        
        benchmark_results[name] = metrics
        print(f"[{name}] Acurácia: {metrics['accuracy']:.4f} | F1: {metrics['f1_score']:.4f} | ROC-AUC: {metrics['roc_auc']:.4f} (CV: {cv_scores.mean():.4f} ± {cv_scores.std():.4f})")
        
        if metrics["roc_auc"] > best_roc_auc:
            best_roc_auc = metrics["roc_auc"]
            best_name = name
            best_pipeline = pipe

    print(f"\n>> Campeão Selecionado: {best_name} (ROC-AUC: {best_roc_auc:.4f})")
    return {
        "best_model_name": best_name,
        "best_pipeline": best_pipeline,
        "benchmark": benchmark_results
    }


def run_training_pipeline() -> Tuple[Pipeline, Dict[str, Any]]:
    """Executa o pipeline completo de treinamento, avaliação e persistência."""
    df = load_or_generate_data()
    X_train, X_test, y_train, y_test = split_data(df)
    
    comparison = train_and_compare_models(X_train, y_train, X_test, y_test)
    best_pipe = comparison["best_pipeline"]
    champion_name = comparison["best_model_name"]
    metrics = comparison["benchmark"][champion_name]

    # Salvar artefatos
    MODEL_PIPELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipe, MODEL_PIPELINE_PATH)
    print(f"Modelo campeão salvo em: {MODEL_PIPELINE_PATH}")

    summary = {
        "model_name": champion_name,
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "metrics": metrics,
        "all_benchmarks": comparison["benchmark"]
    }
    with open(METRICS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Métricas detalhadas salvas em: {METRICS_JSON_PATH}")

    return best_pipe, summary


if __name__ == "__main__":
    run_training_pipeline()
