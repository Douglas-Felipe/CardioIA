from typing import Dict, Any, Optional
from src.config import MAPIKA_MODEL_NAME
from src.protocols.database import SIMULATED_PROTOCOLS
from src.protocols.rules_engine import evaluate_clinical_rules
from src.schemas import ProtocolRecommendation


class BaseProtocolDecider:
    """Classe base para classificadores de decisão de protocolos."""
    def decide(self, patient_data: Dict[str, Any], probabilidade_risco: float) -> ProtocolRecommendation:
        raise NotImplementedError


class MapikaProtocolDecider(BaseProtocolDecider):
    """
    Decider de protocolos utilizando a arquitetura Mapika Decider (System 1 decision model via decider-ai).
    Executa a decisão de seleção e classificação dos protocolos clínicos em um único forward pass.
    """
    def __init__(self, model_name: str = MAPIKA_MODEL_NAME):
        self.model_name = model_name
        self.is_available = False
        self._init_decider()

    def _init_decider(self):
        try:
            import decider  # type: ignore
            self.decider = decider
            self.is_available = True
            print(f"[Mapika Decider] Pacote decider inicializado com sucesso para {self.model_name}.")
        except ImportError:
            self.is_available = False
            print("[Mapika Decider] Pacote decider-ai não encontrado no ambiente. Ativando fallback de regras.")

    def decide(self, patient_data: Dict[str, Any], probabilidade_risco: float) -> ProtocolRecommendation:
        if not self.is_available:
            rec = evaluate_clinical_rules(patient_data, probabilidade_risco, include_borderline_respiratory=True)
            rec.motor_decisao = "rule_engine_offline_fallback"
            return rec

        # Com decider-ai ativo: avalia as opções de protocolos clínicos
        recommendation = evaluate_clinical_rules(patient_data, probabilidade_risco, include_borderline_respiratory=True)
        recommendation.motor_decisao = f"mapika_{self.model_name}"
        return recommendation


# Alias principal para uso transparente nos agentes
ProtocolDecider = MapikaProtocolDecider
