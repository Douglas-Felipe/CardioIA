from typing import Dict, Any, List
from src.protocols.database import PROTOCOL_RULES_METADATA
from src.schemas import ProtocolItem, ProtocolRecommendation


def evaluate_clinical_rules(
    patient_data: Dict[str, Any],
    probabilidade_risco: float = 0.0,
    include_borderline_respiratory: bool = False
) -> ProtocolRecommendation:
    """
    Avalia as regras clínicas simuladas sobre as variáveis do paciente e o risco previsto.
    
    Args:
        patient_data: Dicionário com os atributos clínicos do paciente.
        probabilidade_risco: Probabilidade predita pelo modelo de ML.
        include_borderline_respiratory: Se True, considera SPO2 < 90% para suporte respiratório precoce.
        
    Returns:
        ProtocolRecommendation com os protocolos ativados.
    """
    triggered_rules: List[str] = []
    details: List[ProtocolItem] = []

    # Mesclar probabilidade no dicionário para checagem da regra de emergência
    eval_context = dict(patient_data)
    if "disponibilidade recursos" in eval_context and "disponibilidade_recursos" not in eval_context:
        eval_context["disponibilidade_recursos"] = eval_context["disponibilidade recursos"]
    eval_context["probabilidade_risco"] = probabilidade_risco

    for rule_meta in PROTOCOL_RULES_METADATA:
        param = rule_meta["parametro"]
        op = rule_meta["operador"]
        threshold = rule_meta["limiar"]
        val = eval_context.get(param)

        if val is None:
            continue

        val = float(val)
        is_triggered = False

        if op == "<" and val < threshold:
            is_triggered = True
        elif op == ">" and val > threshold:
            is_triggered = True
        elif op == "<=" and val <= threshold:
            is_triggered = True
        elif op == ">=" and val >= threshold:
            is_triggered = True

        # Suporte precoce a hipoxemia borderline (ex: SpO2 < 90% em casos críticos)
        if param == "spo2_media" and not is_triggered and include_borderline_respiratory and val <= 89.0:
            is_triggered = True

        if is_triggered:
            triggered_rules.append(rule_meta["regra"])
            details.append(ProtocolItem(
                regra=rule_meta["regra"],
                parametro=param,
                valor_observado=val,
                condicao_limiar=f"{op} {threshold}",
                acao_recomendada=rule_meta["acao"]
            ))

    return ProtocolRecommendation(
        protocolos_sugeridos=triggered_rules,
        detalhes=details,
        motor_decisao="rule_engine"
    )
