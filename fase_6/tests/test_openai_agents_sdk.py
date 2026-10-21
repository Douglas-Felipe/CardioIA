import pytest
from src.agents.openai_agents_sdk import (
    create_openai_agent_system,
    orchestrator_agent,
    risk_analyst_agent,
    protocols_specialist_agent,
    response_planner_agent,
    predict_cardiac_risk,
    evaluate_clinical_protocols
)
from src.schemas import FinalTriageResponse


@pytest.mark.unit
def test_openai_agents_sdk_configuration():
    """Valida a configuração oficial dos 4 agentes especializados via OpenAI Agents SDK."""
    system = create_openai_agent_system()
    
    assert "orchestrator" in system
    assert "risk_analyst" in system
    assert "protocols_specialist" in system
    assert "response_planner" in system

    orch = system["orchestrator"]
    risk = system["risk_analyst"]
    proto = system["protocols_specialist"]
    resp = system["response_planner"]

    # Validação dos Nomes dos Agentes
    assert orch.name == "Agente Orquestrador"
    assert risk.name == "Agente Analista de Risco"
    assert proto.name == "Agente Especialista em Protocolos"
    assert resp.name == "Agente Planejador de Resposta"

    # Validação de Saída Estruturada do Planejador
    assert resp.output_type == FinalTriageResponse


@pytest.mark.unit
def test_openai_agents_sdk_handoffs_chain():
    """Valida o padrão Hub-and-Spoke de handoffs nativos do OpenAI Agents SDK."""
    system = create_openai_agent_system()
    
    orch = system["orchestrator"]
    risk = system["risk_analyst"]
    proto = system["protocols_specialist"]
    resp = system["response_planner"]

    # 1. Orquestrador supervisiona e possui handoffs para os três agentes especializados
    assert len(orch.handoffs) == 3
    orch_handoff_names = [h.name for h in orch.handoffs]
    assert "Agente Analista de Risco" in orch_handoff_names
    assert "Agente Especialista em Protocolos" in orch_handoff_names
    assert "Agente Planejador de Resposta" in orch_handoff_names

    # 2. Analista de Risco devolve o controle ao Orquestrador
    assert len(risk.handoffs) == 1
    assert risk.handoffs[0].name == "Agente Orquestrador"

    # 3. Especialista em Protocolos devolve o controle ao Orquestrador
    assert len(proto.handoffs) == 1
    assert proto.handoffs[0].name == "Agente Orquestrador"


@pytest.mark.unit
def test_openai_agents_sdk_function_tools():
    """Valida se as Function Tools do OpenAI Agents SDK estão registradas nos agentes corretos."""
    system = create_openai_agent_system()
    
    risk = system["risk_analyst"]
    proto = system["protocols_specialist"]

    # Analista de Risco deve ter a tool predict_cardiac_risk
    assert len(risk.tools) == 1
    assert risk.tools[0].name == "predict_cardiac_risk"

    # Especialista em Protocolos deve ter a tool evaluate_clinical_protocols
    assert len(proto.tools) == 1
    assert proto.tools[0].name == "evaluate_clinical_protocols"
