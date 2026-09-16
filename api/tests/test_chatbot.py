import pytest
from chatbot.local_assistant_engine import LocalAssistantEngine
from chatbot.watson_client import WatsonAssistantClient


@pytest.fixture
def engine():
    return LocalAssistantEngine()


@pytest.fixture
def client():
    return WatsonAssistantClient()


def test_engine_initialization(engine):
    assert engine.skill_data is not None
    assert "intents" in engine.skill_data
    assert "entities" in engine.skill_data
    assert "dialog_nodes" in engine.skill_data


def test_create_session(engine):
    session_id = engine.create_session()
    assert session_id is not None
    assert len(session_id) > 10
    assert session_id in engine.sessions


def test_detect_saudacao(engine):
    result = engine.process_message("Olá, bom dia assistente")
    assert result["intent"] == "saudacao"
    assert "CardioIA" in result["response"]
    assert result["risk_level"] == "BAIXO_RISCO"


def test_detect_sintomas(engine):
    result = engine.process_message("Estou sentindo uma dor no peito e falta de ar")
    assert result["intent"] in ["informar_sintomas", "emergencia_cardiaca"]
    entity_values = [e["value"] for e in result["entities"]]
    assert "dor_no_peito" in entity_values or "falta_de_ar" in entity_values
    assert result["risk_level"] in ["MODERADO", "ALTO_RISCO"]


def test_detect_emergencia_critica(engine):
    result = engine.process_message("Socorro, acho que estou tendo um infarto com dor forte irradiando para o braço esquerdo")
    assert result["intent"] == "emergencia_cardiaca"
    assert result["risk_level"] == "EMERGENCIA"
    assert "SAMU (192)" in result["response"]


def test_detect_dados_vitais(engine):
    result = engine.process_message("Minha pressão arterial deu 14 por 9 e frequencia cardiaca 80 bpm")
    assert result["intent"] == "informar_dados_vitais"
    assert "Diretrizes Brasileiras de Hipertensão" in result["response"]


def test_detect_prevencao(engine):
    result = engine.process_message("Como prevenir doenças do coração e controlar o colesterol?")
    assert result["intent"] == "duvidas_prevencao"
    assert "Alimentação Cardioprotetora" in result["response"]


def test_detect_fallback_anything_else(engine):
    result = engine.process_message("Qual a cotação do dólar hoje?")
    assert result["intent"] == "anything_else"
    assert "saúde cardiológica" in result["response"]


def test_watson_client_fallback_mode(client):
    res = client.send_message("Olá!")
    assert res is not None
    assert "response" in res
    assert "intent" in res
    assert "session_id" in res
