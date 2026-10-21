import pytest
from src.protocols.decider import MapikaProtocolDecider, ProtocolDecider


@pytest.mark.unit
def test_mapika_decider_initialization():
    """Valida a inicialização do Mapika Decider e disponibilidade do pacote decider-ai."""
    decider = MapikaProtocolDecider()
    assert decider.model_name == "decider-4b"
    assert decider.is_available is True


@pytest.mark.unit
def test_mapika_decider_decision(task_patient_dict):
    """Garante que o Mapika Decider avalia e retorna a recomendação com os protocolos disparados."""
    decider = MapikaProtocolDecider()
    rec = decider.decide(task_patient_dict, 0.91)
    assert len(rec.protocolos_sugeridos) >= 3
    assert "mapika" in rec.motor_decisao
    assert any("carga do sistema" in p for p in rec.protocolos_sugeridos)


@pytest.mark.integration
def test_protocol_decider_alias(task_patient_dict):
    """Garante que a classe principal ProtocolDecider opera perfeitamente com os agentes."""
    decider = ProtocolDecider()
    rec = decider.decide(task_patient_dict, 0.91)
    assert len(rec.protocolos_sugeridos) > 0
    assert any("disponibilidade_recursos < 30%" in p for p in rec.protocolos_sugeridos)
