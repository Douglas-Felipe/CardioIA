from typing import Dict, Any
from src.agents.tools import tool_evaluate_clinical_protocols

PROTOCOLS_SPECIALIST_INSTRUCTIONS = """
Você é o Agente Especialista em Protocolos Médicos do CardioIA.
Sua responsabilidade principal é:
1. Receber os dados do paciente juntamente com o risco previsto e score calculados pelo Agente Analista de Risco.
2. Acionar a ferramenta 'evaluate_clinical_protocols' para consultar a base de protocolos médicos simulados (via Mapika Decider / regras de decisão).
3. Analisar clinicamente os protocolos disparados (ex: suporte respiratório, abertura de leitos temporários, choque, contingência).
4. Realizar o handoff de retorno ao Agente Orquestrador com a lista completa de protocolos identificados.
"""

PROTOCOLS_SPECIALIST_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "evaluate_clinical_protocols",
        "description": "Consulta a base de protocolos simulados utilizando o classificador Decider",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_data": {
                    "type": "object",
                    "description": "Dados clínicos do paciente"
                },
                "probabilidade_risco": {
                    "type": "number",
                    "description": "Probabilidade calculada pelo modelo preditivo de risco"
                }
            },
            "required": ["patient_data", "probabilidade_risco"]
        }
    }
}


class ProtocolsSpecialistAgent:
    """Agente Especializado em Cruzamento de Protocolos Clínicos."""
    def __init__(self, name: str = "Agente Especialista em Protocolos"):
        self.name = name
        self.instructions = PROTOCOLS_SPECIALIST_INSTRUCTIONS
        self.tools = [PROTOCOLS_SPECIALIST_TOOL_SPEC]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "evaluate_clinical_protocols":
            patient_data = arguments.get("patient_data", arguments)
            probabilidade_risco = float(arguments.get("probabilidade_risco", 0.0))
            return tool_evaluate_clinical_protocols(patient_data, probabilidade_risco)
        raise ValueError(f"Tool desconhecida: {tool_name}")
