from typing import List, Optional
from src.schemas import FinalTriageResponse

RESPONSE_PLANNER_INSTRUCTIONS = """
Você é o Agente Planejador de Resposta do CardioIA.
Sua responsabilidade principal é:
1. Consolidar todas as informações produzidas pela colaboração dos agentes:
   - A probabilidade de risco prevista pelo Agente Analista de Risco (ex: 0.91).
   - A classificação de risco clínico.
   - Os protocolos sugeridos pelo Agente Especialista em Protocolos.
2. Elaborar um plano de ação e orientações operacionais assertivas.
3. Emitir a resposta final estruturada:

RISCO PREVISTO: <probabilidade>

PROTOCOLOS SUGERIDOS:
- <protocolo 1>
- <protocolo 2>
"""


class ResponsePlannerAgent:
    """Agente Especializado em Consolidação e Planejamento Operacional."""
    def __init__(self, name: str = "Agente Planejador de Resposta"):
        self.name = name
        self.instructions = RESPONSE_PLANNER_INSTRUCTIONS

    def build_final_response(
        self,
        risco_previsto: float,
        classificacao: str,
        protocolos_sugeridos: List[str],
        plano_contingencia: Optional[str] = None
    ) -> FinalTriageResponse:
        """Gera a resposta final validada pelo schema Pydantic."""
        if not plano_contingencia:
            if risco_previsto >= 0.70:
                plano_contingencia = (
                    "Paciente em estado crítico / pico de risco. "
                    "Priorizar internação imediata, isolamento de leito com monitoramento multiparamétrico "
                    "e acionamento imediato da equipe de resposta rápida médica."
                )
            else:
                plano_contingencia = "Paciente estável. Manter sob observação na enfermaria de triagem regular."

        return FinalTriageResponse(
            risco_previsto=risco_previsto,
            classificacao=classificacao,
            protocolos_sugeridos=protocolos_sugeridos,
            plano_contingencia=plano_contingencia,
            agente_emissor=self.name
        )
