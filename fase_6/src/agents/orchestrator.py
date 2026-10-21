from typing import Dict, Any, Optional

ORCHESTRATOR_INSTRUCTIONS = """
Você é o Agente Orquestrador e Supervisor Central do CardioIA.
Sua responsabilidade é atuar como o Hub Central de Decisão do sistema:
1. Receber os dados clínicos de admissão do paciente.
2. Analisar o estado inicial e acionar (handoff) o Agente Analista de Risco para inferência preditiva via Machine Learning.
3. Receber o retorno do Analista de Risco, avaliar a severidade do score e probabilidade calculados, e decidir dinamicamente se o caso exige acionamento imediato do Agente Especialista em Protocolos.
4. Receber o relatório do Especialista em Protocolos, auditar as regras e protocolos ativados via Mapika Decider e verificar se todas as evidências estão consolidadas.
5. Fazer o handoff do dossiê completo para o Agente Planejador de Resposta para elaboração da recomendação formal e plano de contingência.
"""


class OrchestratorAgent:
    """
    Agente Orquestrador Centralizador (Hub-and-Spoke Supervisor).
    Centraliza todas as decisões de roteamento e despacho dos agentes especializados.
    """
    def __init__(self, name: str = "Agente Orquestrador"):
        self.name = name
        self.instructions = ORCHESTRATOR_INSTRUCTIONS

    def decide_next_step(
        self,
        patient_data: Dict[str, Any],
        risk_result: Optional[Dict[str, Any]] = None,
        protocols_result: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Decide de forma centralizada qual o próximo agente a ser acionado com base
        no estado clínico acumulado e nas respostas dos agentes anteriores.
        
        Returns:
            Nome do próximo agente: 'risk_analyst', 'protocols_specialist', 'response_planner' ou 'finish'.
        """
        # Se ainda não temos o risco avaliado pelo modelo preditivo de ML
        if risk_result is None:
            return "risk_analyst"

        # Com o risco calculado, o orquestrador avalia a necessidade de cruzar com protocolos
        if protocols_result is None:
            # Casos com qualquer sinal de risco ou variáveis críticas acionam o Especialista em Protocolos
            return "protocols_specialist"

        # Com risco e protocolos apurados, despacha para consolidação do Planejador
        return "response_planner"
