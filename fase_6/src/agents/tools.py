from typing import Dict, Any
from src.ml.predictor import CardiacRiskPredictor
from src.protocols.decider import ProtocolDecider

# Instâncias singleton para reutilização rápida
_predictor = None
_decider = None


def get_predictor() -> CardiacRiskPredictor:
    global _predictor
    if _predictor is None:
        _predictor = CardiacRiskPredictor()
    return _predictor


def get_decider() -> ProtocolDecider:
    global _decider
    if _decider is None:
        _decider = ProtocolDecider()
    return _decider


def tool_predict_cardiac_risk(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool do Agente Analista de Risco: Consulta o modelo preditivo supervisionado salvo (joblib)
    e retorna o score de risco, probabilidade calibrada e classificação clínica.
    """
    predictor = get_predictor()
    pred = predictor.predict(patient_data)
    return pred.model_dump()


def tool_evaluate_clinical_protocols(patient_data: Dict[str, Any], probabilidade_risco: float) -> Dict[str, Any]:
    """
    Tool do Agente Especialista em Protocolos: Consulta a base de protocolos simulados
    utilizando o classificador Mapika Decider 4B para selecionar os protocolos clínicos
    e operacionais aplicáveis ao paciente.
    """
    decider = get_decider()
    rec = decider.decide(patient_data, probabilidade_risco)
    return rec.model_dump()
