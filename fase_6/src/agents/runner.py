from typing import Dict, Any, List, Optional
import json

from src.schemas import PatientData, FinalTriageResponse, RiskPrediction, ProtocolRecommendation
from src.agents.orchestrator import OrchestratorAgent
from src.agents.risk_analyst import RiskAnalystAgent
from src.agents.protocols_specialist import ProtocolsSpecialistAgent
from src.agents.response_planner import ResponsePlannerAgent


class AgentMessage:
    """Representa um registro no histórico de mensagens do pipeline multiagente."""
    def __init__(self, sender: str, recipient: str, message_type: str, content: Any):
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type  # 'input', 'decision', 'handoff', 'tool_call', 'tool_result', 'final_output'
        self.content = content

    def __repr__(self):
        return f"[{self.message_type.upper()}] {self.sender} -> {self.recipient}: {self.content}"


class MultiAgentPipelineRunner:
    """
    Runner da arquitetura Multiagente Centralizada (Hub-and-Spoke Orchestrator).
    Todas as decisões de roteamento entre agentes são centralizadas no Agente Orquestrador:
    1. Orquestrador decide e despacha -> Analista de Risco
    2. Analista de Risco conclui inferência -> reporta de volta ao Orquestrador
    3. Orquestrador analisa o risco predito e decide acionar -> Especialista em Protocolos
    4. Especialista em Protocolos conclui avaliação via Mapika -> reporta de volta ao Orquestrador
    5. Orquestrador audita o dossiê completo e despacha -> Planejador de Resposta
    """

    def __init__(self, *args, **kwargs):
        self.orchestrator = OrchestratorAgent()
        self.risk_analyst = RiskAnalystAgent()
        self.protocols_specialist = ProtocolsSpecialistAgent()
        self.response_planner = ResponsePlannerAgent()
        self.history: List[AgentMessage] = []

    def log_event(self, sender: str, recipient: str, message_type: str, content: Any):
        msg = AgentMessage(sender=sender, recipient=recipient, message_type=message_type, content=content)
        self.history.append(msg)
        return msg

    def run(self, patient_input: Any) -> FinalTriageResponse:
        """
        Executa o pipeline multiagente centralizado para o paciente fornecido.
        """
        self.history.clear()

        # 1. Validação de entrada via Pydantic
        if isinstance(patient_input, PatientData):
            patient = patient_input
        elif isinstance(patient_input, dict):
            patient = PatientData(**patient_input)
        else:
            patient = PatientData(**patient_input.iloc[0].to_dict())

        patient_dict = patient.to_features_dict()

        # ETAPA 1: Entrada do paciente no sistema e recepção pelo Orquestrador
        self.log_event(
            sender="Usuário / Sistema Hospitalar",
            recipient=self.orchestrator.name,
            message_type="input",
            content=f"Novo paciente recebido para triagem: SpO2={patient.spo2_media}%, FC={patient.fc_media} bpm, Carga={patient.carga_sistema}%"
        )

        # DECISÃO CENTRAL 1: Orquestrador analisa o estado inicial e decide acionar o Analista de Risco
        decision_1 = self.orchestrator.decide_next_step(patient_dict)
        self.log_event(
            sender=self.orchestrator.name,
            recipient=self.orchestrator.name,
            message_type="decision",
            content="Orquestrador avalia dados clínicos iniciais e decide acionar o Agente Analista de Risco para cálculo do score preditivo de ML."
        )

        # Handoff 1: Orquestrador -> Analista de Risco
        self.log_event(
            sender=self.orchestrator.name,
            recipient=self.risk_analyst.name,
            message_type="handoff",
            content="Orquestrador despacha paciente para análise preditiva supervisionada."
        )

        # ETAPA 2: Analista de Risco executa Tool de Machine Learning
        self.log_event(
            sender=self.risk_analyst.name,
            recipient="Tool: predict_cardiac_risk",
            message_type="tool_call",
            content="Invocando modelo preditivo supervisionado (Random Forest Pipeline / Joblib)"
        )
        risk_result_dict = self.risk_analyst.execute_tool(
            "predict_cardiac_risk",
            {"patient_data": patient_dict}
        )
        risk_pred = RiskPrediction(**risk_result_dict)
        self.log_event(
            sender="Tool: predict_cardiac_risk",
            recipient=self.risk_analyst.name,
            message_type="tool_result",
            content=f"Probabilidade calculada: {risk_pred.probabilidade_risco:.2f} ({risk_pred.classificacao_texto}), Risk Score Base={risk_pred.score_regras_base}"
        )

        # Handoff 2 (Retorno): Analista de Risco reporta laudo de volta ao Orquestrador
        self.log_event(
            sender=self.risk_analyst.name,
            recipient=self.orchestrator.name,
            message_type="handoff",
            content=f"Laudo concluído: Risco={risk_pred.probabilidade_risco:.2f} ({risk_pred.classificacao_texto}). Devolvendo controle ao Orquestrador."
        )

        # DECISÃO CENTRAL 2: Orquestrador analisa a predição de risco e decide acionar o Especialista em Protocolos
        decision_2 = self.orchestrator.decide_next_step(patient_dict, risk_result=risk_result_dict)
        self.log_event(
            sender=self.orchestrator.name,
            recipient=self.orchestrator.name,
            message_type="decision",
            content=(
                f"Orquestrador analisa laudo de risco ({risk_pred.classificacao_texto}, probabilidade {risk_pred.probabilidade_risco:.2f}). "
                "Decide acionar o Agente Especialista em Protocolos para cruzamento com a base de protocolos clínicos simulados."
            )
        )

        # Handoff 3: Orquestrador -> Especialista em Protocolos
        self.log_event(
            sender=self.orchestrator.name,
            recipient=self.protocols_specialist.name,
            message_type="handoff",
            content="Orquestrador despacha caso e score de risco para cruzamento de protocolos hospitalares."
        )

        # ETAPA 3: Especialista em Protocolos executa Tool Decider (Mapika Decider 4B)
        self.log_event(
            sender=self.protocols_specialist.name,
            recipient="Tool: evaluate_clinical_protocols",
            message_type="tool_call",
            content="Avaliando base de protocolos simulados utilizando o Mapika Decider 4B"
        )
        protocols_result_dict = self.protocols_specialist.execute_tool(
            "evaluate_clinical_protocols",
            {"patient_data": patient_dict, "probabilidade_risco": risk_pred.probabilidade_risco}
        )
        protocols_rec = ProtocolRecommendation(**protocols_result_dict)
        self.log_event(
            sender="Tool: evaluate_clinical_protocols",
            recipient=self.protocols_specialist.name,
            message_type="tool_result",
            content=f"{len(protocols_rec.protocolos_sugeridos)} protocolos identificados via motor {protocols_rec.motor_decisao}"
        )

        # Handoff 4 (Retorno): Especialista em Protocolos reporta protocolos ao Orquestrador
        self.log_event(
            sender=self.protocols_specialist.name,
            recipient=self.orchestrator.name,
            message_type="handoff",
            content=f"Protocolos apurados ({len(protocols_rec.protocolos_sugeridos)} ativos). Devolvendo controle ao Orquestrador."
        )

        # DECISÃO CENTRAL 3: Orquestrador audita evidências e despacha para o Planejador de Resposta
        decision_3 = self.orchestrator.decide_next_step(patient_dict, risk_result=risk_result_dict, protocols_result=protocols_result_dict)
        self.log_event(
            sender=self.orchestrator.name,
            recipient=self.orchestrator.name,
            message_type="decision",
            content=(
                f"Orquestrador audita dossiê completo (Risco: {risk_pred.probabilidade_risco:.2f} + {len(protocols_rec.protocolos_sugeridos)} protocolos). "
                "Decide acionar o Agente Planejador de Resposta para síntese executiva e formatação da recomendação final."
            )
        )

        # Handoff 5: Orquestrador -> Planejador de Resposta
        self.log_event(
            sender=self.orchestrator.name,
            recipient=self.response_planner.name,
            message_type="handoff",
            content="Orquestrador transfere dossiê final consolidado para elaboração do plano de ação e contingência."
        )

        # ETAPA 4: Planejador de Resposta estrutura a recomendação final
        final_response = self.response_planner.build_final_response(
            risco_previsto=risk_pred.probabilidade_risco,
            classificacao=risk_pred.classificacao_texto,
            protocolos_sugeridos=protocols_rec.protocolos_sugeridos
        )

        self.log_event(
            sender=self.response_planner.name,
            recipient="Usuário / Equipe Médica",
            message_type="final_output",
            content=final_response.format_task_output()
        )

        return final_response
