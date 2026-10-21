import pytest
from src.protocols.rules_engine import evaluate_clinical_rules
from src.protocols.database import SIMULATED_PROTOCOLS, PROTOCOL_RULES_METADATA


@pytest.mark.unit
def test_simulated_protocols_count():
    """Garante que todos os 10 protocolos exigidos estejam cadastrados."""
    assert len(SIMULATED_PROTOCOLS) == 10
    assert len(PROTOCOL_RULES_METADATA) == 10


@pytest.mark.unit
def test_rule_spo2_boundary():
    """Testa a regra de SpO2 < 88%."""
    # 87.9 deve disparar
    rec_trigger = evaluate_clinical_rules({"spo2_media": 87.9})
    assert any("SPO2 < 88%" in r for r in rec_trigger.protocolos_sugeridos)

    # 88.1 não deve disparar em modo normal
    rec_no_trigger = evaluate_clinical_rules({"spo2_media": 88.1}, include_borderline_respiratory=False)
    assert not any("SPO2 < 88%" in r for r in rec_no_trigger.protocolos_sugeridos)


@pytest.mark.unit
def test_rule_carga_sistema_boundary():
    """Testa a regra de carga do sistema > 85%."""
    rec_trigger = evaluate_clinical_rules({"carga_sistema": 85.5})
    assert any("carga do sistema > 85%" in r for r in rec_trigger.protocolos_sugeridos)

    rec_no_trigger = evaluate_clinical_rules({"carga_sistema": 84.9})
    assert not any("carga do sistema > 85%" in r for r in rec_no_trigger.protocolos_sugeridos)


@pytest.mark.unit
def test_rule_disponibilidade_recursos_boundary():
    """Testa a regra de disponibilidade de recursos < 30%."""
    rec_trigger = evaluate_clinical_rules({"disponibilidade_recursos": 29.9})
    assert any("disponibilidade_recursos < 30%" in r for r in rec_trigger.protocolos_sugeridos)

    rec_no_trigger = evaluate_clinical_rules({"disponibilidade_recursos": 30.1})
    assert not any("disponibilidade_recursos < 30%" in r for r in rec_no_trigger.protocolos_sugeridos)


@pytest.mark.unit
def test_task_patient_protocols_triggered(task_patient_dict):
    """Valida se os protocolos disparados para o caso oficial contêm os protocolos essenciais"""
    rec = evaluate_clinical_rules(task_patient_dict, probabilidade_risco=0.91, include_borderline_respiratory=True)
    
    # Validações dos protocolos exibidos no exemplo:
    assert any("carga do sistema > 85%" in r for r in rec.protocolos_sugeridos)
    assert any("SPO2 < 88%" in r for r in rec.protocolos_sugeridos)
    assert any("disponibilidade_recursos < 30%" in r for r in rec.protocolos_sugeridos)
