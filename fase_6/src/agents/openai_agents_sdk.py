"""
Configuração e Estruturação do Sistema Multiagente utilizando o OPENAI AGENTS SDK oficial.
Este módulo define os 4 Agentes Especializados, as Function Tools e os Handoffs Nativos
"""

from typing import Dict, Any, Optional
from agents import Agent, Runner, function_tool, handoff

from src.schemas import PatientData, FinalTriageResponse, RiskPrediction, ProtocolRecommendation
from src.agents.tools import tool_predict_cardiac_risk, tool_evaluate_clinical_protocols
from src.agents.risk_analyst import RISK_ANALYST_INSTRUCTIONS
from src.agents.protocols_specialist import PROTOCOLS_SPECIALIST_INSTRUCTIONS
from src.agents.response_planner import RESPONSE_PLANNER_INSTRUCTIONS
from src.agents.orchestrator import ORCHESTRATOR_INSTRUCTIONS


# ---------------------------------------------------------------------------
# 1. FUNCTION TOOLS DO OPENAI AGENTS SDK
# ---------------------------------------------------------------------------

@function_tool(strict_mode=False)
def predict_cardiac_risk(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool do Agente Analista de Risco (OpenAI Agents SDK):
    Consulta o modelo supervisionado de Machine Learning salvo (Random Forest / Joblib)
    e retorna o score de risco, probabilidade calibrada e classificação clínica.
    """
    return tool_predict_cardiac_risk(patient_data)


@function_tool(strict_mode=False)
def evaluate_clinical_protocols(patient_data: Dict[str, Any], probabilidade_risco: float) -> Dict[str, Any]:
    """
    Tool do Agente Especialista em Protocolos (OpenAI Agents SDK):
    Consulta a base de protocolos simulados utilizando o classificador de decisão rápida
    Mapika Decider 4B (decider-ai) para selecionar os protocolos clínicos e operacionais aplicáveis.
    """
    return tool_evaluate_clinical_protocols(patient_data, probabilidade_risco)


# ---------------------------------------------------------------------------
# 2. DEFINIÇÃO DOS 4 AGENTES ESPECIALIZADOS E HANDOFFS NATIVOS
# ---------------------------------------------------------------------------

def create_openai_agent_system(model: str = "gpt-4o-mini") -> Dict[str, Agent]:
    """
    Instancia e interliga os 4 agentes especializados no padrão Hub-and-Spoke Centralizado:
    O Agente Orquestrador centraliza todas as decisões e despachos:
    1. Orquestrador -> Analista de Risco -> Orquestrador
    2. Orquestrador -> Especialista em Protocolos -> Orquestrador
    3. Orquestrador -> Planejador de Resposta (Saída Final)
    """

    # Agente 1: Orquestrador (Supervisor Central)
    orchestrator_agent = Agent(
        name="Agente Orquestrador",
        model=model,
        instructions=ORCHESTRATOR_INSTRUCTIONS
    )

    # Agente 4: Planejador de Resposta (Consolida recomendações e valida saída Pydantic)
    response_planner_agent = Agent(
        name="Agente Planejador de Resposta",
        model=model,
        instructions=RESPONSE_PLANNER_INSTRUCTIONS,
        output_type=FinalTriageResponse
    )

    # Agente 3: Especialista em Protocolos (Avalia protocolos via Mapika Decider e retorna ao Orquestrador)
    protocols_specialist_agent = Agent(
        name="Agente Especialista em Protocolos",
        model=model,
        instructions=PROTOCOLS_SPECIALIST_INSTRUCTIONS,
        tools=[evaluate_clinical_protocols],
        handoffs=[orchestrator_agent]
    )

    # Agente 2: Analista de Risco (Executa o modelo preditivo de ML e retorna ao Orquestrador)
    risk_analyst_agent = Agent(
        name="Agente Analista de Risco",
        model=model,
        instructions=RISK_ANALYST_INSTRUCTIONS,
        tools=[predict_cardiac_risk],
        handoffs=[orchestrator_agent]
    )

    # O Orquestrador supervisiona e possui handoffs para os três agentes especializados
    orchestrator_agent.handoffs = [
        risk_analyst_agent,
        protocols_specialist_agent,
        response_planner_agent
    ]

    return {
        "orchestrator": orchestrator_agent,
        "risk_analyst": risk_analyst_agent,
        "protocols_specialist": protocols_specialist_agent,
        "response_planner": response_planner_agent,
    }


# Instância padrão dos agentes
AGENTS_SYSTEM = create_openai_agent_system()
orchestrator_agent = AGENTS_SYSTEM["orchestrator"]
risk_analyst_agent = AGENTS_SYSTEM["risk_analyst"]
protocols_specialist_agent = AGENTS_SYSTEM["protocols_specialist"]
response_planner_agent = AGENTS_SYSTEM["response_planner"]
