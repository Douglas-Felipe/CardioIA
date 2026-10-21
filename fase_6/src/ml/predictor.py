from pathlib import Path
from typing import Union, Dict, Any
import numpy as np
import pandas as pd
import joblib

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.config import MODEL_PIPELINE_PATH
from src.schemas import PatientData, RiskPrediction
from src.ml.train import FEATURE_COLUMNS


def calculate_base_risk_score(data: Dict[str, Any]) -> int:
    """Calcula o risk_score"""
    val_recursos = data.get("disponibilidade_recursos")
    if val_recursos is None:
        val_recursos = data.get("disponibilidade recursos", 100)

    carga = float(data.get("carga_sistema", 0)) > 80
    espera = float(data.get("tempo_espera", 0)) > 60
    spo2 = float(data.get("spo2_media", 100)) < 92
    fc = float(data.get("fc_media", 0)) > 110
    eventos = float(data.get("eventos_24h", 0)) > 4
    recursos = float(val_recursos) < 40
    
    score = int(carga) + int(espera) + int(spo2) + int(fc) + int(eventos) + int(recursos)
    return score


class CardiacRiskPredictor:
    """Carrega o pipeline serializado e executa inferências de risco cardíaco."""

    def __init__(self, model_path: Union[str, Path] = MODEL_PIPELINE_PATH):
        self.model_path = Path(model_path)
        self.pipeline = self._load_model()

    def _load_model(self):
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Modelo treinado não encontrado em: {self.model_path}. "
                "Execute primeiro 'python src/ml/train.py'."
            )
        return joblib.load(self.model_path)

    def predict(self, patient: Union[PatientData, Dict[str, Any], pd.DataFrame]) -> RiskPrediction:
        """
        Executa a predição para um paciente e retorna o RiskPrediction Pydantic.
        """
        if isinstance(patient, PatientData):
            features_dict = patient.to_features_dict()
        elif isinstance(patient, pd.DataFrame):
            # Normalizar se colunas tiverem espaço
            clean_df = patient.rename(columns={"disponibilidade recursos": "disponibilidade_recursos"})
            features_dict = clean_df.iloc[0].to_dict()
        else:
            if "disponibilidade recursos" in patient and "disponibilidade_recursos" not in patient:
                patient["disponibilidade_recursos"] = patient["disponibilidade recursos"]
            features_dict = patient

        # Montar DataFrame ordenado para o scikit-learn
        df_input = pd.DataFrame([[features_dict[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)

        # Probabilidade prevista da classe 1 (pico de risco)
        probas = self.pipeline.predict_proba(df_input)[0]
        prob_risk = float(probas[1])
        binary_pred = int(self.pipeline.predict(df_input)[0])

        score_base = calculate_base_risk_score(features_dict)

        if prob_risk >= 0.70:
            classificacao = "ALTO RISCO"
        elif prob_risk >= 0.35:
            classificacao = "RISCO MODERADO"
        else:
            classificacao = "BAIXO RISCO"

        return RiskPrediction(
            probabilidade_risco=round(prob_risk, 4),
            pico_risco=binary_pred,
            classificacao_texto=classificacao,
            score_regras_base=score_base
        )
