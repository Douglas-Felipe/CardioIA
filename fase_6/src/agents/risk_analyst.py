from typing import Dict, Any
from src.agents.tools import tool_predict_cardiac_risk

RISK_ANALYST_INSTRUCTIONS = """
Você é o Agente Analista de Risco Cardíaco do CardioIA.
Sua responsabilidade principal é:
1. Receber os dados clínicos e operacionais do paciente.
2. Acionar a ferramenta 'predict_cardiac_risk' para consultar o modelo preditivo de Machine Learning treinado.
3. Extrair a probabilidade calculada de pico de risco, a classificação clínica (ex: ALTO RISCO) e o risk_score base.
4. Compartilhar formalmente o laudo preditivo e realizar o handoff de retorno para o Agente Orquestrador.
"""

RISK_ANALYST_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "predict_cardiac_risk",
        "description": "Consulta o modelo preditivo supervisionado de risco cardíaco (joblib pipeline)",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_data": {
                    "type": "object",
                    "description": "Dados clínicos contendo idade, carga_sistema, tempo_espera, fc_media, spo2_media, pa_sistolica, temperatura, etc."
                }
            },
            "required": ["patient_data"]
        }
    }
}


class RiskAnalystAgent:
    """Agente Especializado em Análise Preditiva de Risco Cardíaco."""
    def __init__(self, name: str = "Agente Analista de Risco"):
        self.name = name
        self.instructions = RISK_ANALYST_INSTRUCTIONS
        self.tools = [RISK_ANALYST_TOOL_SPEC]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name == "predict_cardiac_risk":
            patient_data = arguments.get("patient_data", arguments)
            return tool_predict_cardiac_risk(patient_data)
        raise ValueError(f"Tool desconhecida: {tool_name}")
