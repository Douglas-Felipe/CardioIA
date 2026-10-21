import pytest
from src.agents.runner import MultiAgentPipelineRunner
from src.schemas import FinalTriageResponse


@pytest.mark.integration
def test_multiagent_full_pipeline_flow(task_patient_dict):
    """Testa a esteira completa dos 4 agentes com handoffs e tools."""
    runner = MultiAgentPipelineRunner(use_llm_if_available=False)
    response = runner.run(task_patient_dict)
    
    assert isinstance(response, FinalTriageResponse)
    assert 0.0 <= response.risco_previsto <= 1.0
    assert len(response.protocolos_sugeridos) > 0
    assert response.agente_emissor == "Agente Planejador de Resposta"

    # Verificar se os handoffs e eventos foram devidamente registrados no histórico
    history_types = [msg.message_type for msg in runner.history]
    assert "input" in history_types
    assert history_types.count("decision") == 3 # 3 decisões centrais tomadas pelo Orquestrador
    assert history_types.count("handoff") == 5  # Hub-and-Spoke: Orch -> Risk -> Orch -> Proto -> Orch -> Resp
    assert history_types.count("tool_call") == 2 # ML e Decider
    assert history_types.count("tool_result") == 2
    assert "final_output" in history_types


@pytest.mark.integration
def test_multiagent_handoff_sequence(task_patient_dict):
    """Garante a ordem exata de handoffs centralizados no Orquestrador (Hub-and-Spoke)."""
    runner = MultiAgentPipelineRunner(use_llm_if_available=False)
    runner.run(task_patient_dict)
    
    handoffs = [msg for msg in runner.history if msg.message_type == "handoff"]
    assert len(handoffs) == 5
    
    # 1º Handoff: Orquestrador -> Analista de Risco
    assert handoffs[0].sender == "Agente Orquestrador"
    assert handoffs[0].recipient == "Agente Analista de Risco"
    
    # 2º Handoff: Analista de Risco -> Orquestrador (Retorno do laudo)
    assert handoffs[1].sender == "Agente Analista de Risco"
    assert handoffs[1].recipient == "Agente Orquestrador"
    
    # 3º Handoff: Orquestrador -> Especialista em Protocolos
    assert handoffs[2].sender == "Agente Orquestrador"
    assert handoffs[2].recipient == "Agente Especialista em Protocolos"

    # 4º Handoff: Especialista em Protocolos -> Orquestrador (Retorno dos protocolos)
    assert handoffs[3].sender == "Agente Especialista em Protocolos"
    assert handoffs[3].recipient == "Agente Orquestrador"

    # 5º Handoff: Orquestrador -> Planejador de Resposta
    assert handoffs[4].sender == "Agente Orquestrador"
    assert handoffs[4].recipient == "Agente Planejador de Resposta"
