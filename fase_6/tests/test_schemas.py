import pytest
from pydantic import ValidationError
from src.schemas import PatientData, RiskPrediction, ProtocolRecommendation, FinalTriageResponse


@pytest.mark.unit
def test_patient_data_alias_handling():
    """Valida se 'disponibilidade recursos' (com espaço) é convertido corretamente para 'disponibilidade_recursos'."""
    data = {
        "idade_media": 50,
        "carga_sistema": 80,
        "tempo_espera": 30,
        "fc_media": 75,
        "spo2_media": 98,
        "pa_sistolica": 120,
        "temperatura": 36.5,
        "densidade_eventos": 2,
        "eventos_24h": 1,
        "disponibilidade recursos": 70
    }
    patient = PatientData(**data)
    assert patient.disponibilidade_recursos == 70.0


@pytest.mark.unit
def test_patient_data_validation_bounds():
    """Garante que parâmetros biológicos/operacionais inválidos lançam ValidationError."""
    with pytest.raises(ValidationError):
        # SpO2 não pode ser > 100%
        PatientData(
            idade_media=50,
            carga_sistema=50,
            tempo_espera=10,
            fc_media=80,
            spo2_media=120,
            pa_sistolica=120,
            temperatura=36.5,
            densidade_eventos=1,
            eventos_24h=1,
            disponibilidade_recursos=50
        )


@pytest.mark.unit
def test_final_response_formatting():
    """Valida se o formato textual exigido é reproduzido."""
    resp = FinalTriageResponse(
        risco_previsto=0.91,
        classificacao="ALTO RISCO",
        protocolos_sugeridos=[
            "Se carga do sistema > 85% → abrir unidades temporárias",
            "Se SPO2 < 88% → iniciar suporte respiratório imediato",
            "Se disponibilidade_recursos < 30% → redistribuir insumos"
        ]
    )
    output = resp.format_task_output()
    assert "RISCO PREVISTO: 0.91" in output
    assert "PROTOCOLOS SUGERIDOS:" in output
    assert "- Se carga do sistema > 85% → abrir unidades temporárias" in output
    assert "- Se SPO2 < 88% → iniciar suporte respiratório imediato" in output
    assert "- Se disponibilidade_recursos < 30% → redistribuir insumos" in output
