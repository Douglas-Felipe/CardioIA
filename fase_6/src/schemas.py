from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class PatientData(BaseModel):
    """Dados clínicos e operacionais do paciente para triagem de risco cardíaco."""
    idade_media: float = Field(..., description="Idade média do paciente (em anos)", ge=0, le=120)
    carga_sistema: float = Field(..., description="Carga operacional do sistema hospitalar (%)", ge=0, le=100)
    tempo_espera: float = Field(..., description="Tempo de espera na triagem (em minutos)", ge=0)
    fc_media: float = Field(..., description="Frequência cardíaca média (bpm)", ge=20, le=300)
    spo2_media: float = Field(..., description="Saturação periférica de oxigênio SpO2 (%)", ge=50, le=100)
    pa_sistolica: float = Field(..., description="Pressão arterial sistólica (mmHg)", ge=40, le=300)
    temperatura: float = Field(..., description="Temperatura corporal (°C)", ge=25, le=45)
    densidade_eventos: float = Field(..., description="Densidade de eventos adversos na unidade", ge=0)
    eventos_24h: float = Field(..., description="Quantidade de eventos graves nas últimas 24h", ge=0)
    disponibilidade_recursos: float = Field(
        ...,
        description="Disponibilidade de recursos/insumos na unidade (%)",
        ge=0,
        le=100
    )

    @model_validator(mode="before")
    @classmethod
    def handle_field_aliases(cls, data):
        """Permite lidar com variações de nomes como 'disponibilidade recursos'."""
        if isinstance(data, dict):
            if "disponibilidade recursos" in data and "disponibilidade_recursos" not in data:
                data["disponibilidade_recursos"] = data["disponibilidade recursos"]
        return data

    def to_features_dict(self) -> dict:
        """Retorna as features na ordem esperada pelo modelo preditivo."""
        return {
            "idade_media": self.idade_media,
            "carga_sistema": self.carga_sistema,
            "tempo_espera": self.tempo_espera,
            "fc_media": self.fc_media,
            "spo2_media": self.spo2_media,
            "pa_sistolica": self.pa_sistolica,
            "temperatura": self.temperatura,
            "densidade_eventos": self.densidade_eventos,
            "eventos_24h": self.eventos_24h,
            "disponibilidade_recursos": self.disponibilidade_recursos,
        }


class RiskPrediction(BaseModel):
    """Resultado da predição do modelo de Machine Learning."""
    probabilidade_risco: float = Field(..., description="Probabilidade calibrada de pico de risco (0.0 a 1.0)", ge=0.0, le=1.0)
    pico_risco: int = Field(..., description="Classificação binária (0 = normal, 1 = pico de risco)", ge=0, le=1)
    classificacao_texto: str = Field(..., description="Texto da classificação (ex: ALTO RISCO, RISCO MODERADO, BAIXO RISCO)")
    score_regras_base: int = Field(..., description="Risk score calculado pelas regras base da atividade")


class ProtocolItem(BaseModel):
    """Protocolo clínico sugerido com justificativa."""
    regra: str = Field(..., description="Texto descritivo da regra do protocolo")
    parametro: str = Field(..., description="Parâmetro clínico disparador")
    valor_observado: float = Field(..., description="Valor observado no paciente")
    condicao_limiar: str = Field(..., description="Condição de disparo (ex: > 85%, < 88%)")
    acao_recomendada: str = Field(..., description="Ação médica ou operacional imediata recomendada")


class ProtocolRecommendation(BaseModel):
    """Conjunto de protocolos clínicos e operacionais sugeridos."""
    protocolos_sugeridos: List[str] = Field(
        default_factory=list,
        description="Lista textual dos protocolos disparados"
    )
    detalhes: List[ProtocolItem] = Field(
        default_factory=list,
        description="Detalhes estruturados de cada protocolo disparado"
    )
    motor_decisao: str = Field(
        default="mapika_decider_4b",
        description="Motor utilizado na decisão: mapika_decider_4b ou rule_engine_fallback"
    )


class FinalTriageResponse(BaseModel):
    """Recomendação final consolidada pelo pipeline multiagente."""
    risco_previsto: float = Field(..., description="Probabilidade de risco prevista pelo modelo de ML (ex: 0.91)")
    classificacao: str = Field(..., description="Classificação textual de risco")
    protocolos_sugeridos: List[str] = Field(..., description="Lista de protocolos médicos sugeridos")
    plano_contingencia: Optional[str] = Field(None, description="Orientações e plano de ação operacional consolidado")
    agente_emissor: str = Field(default="Agente Planejador de Resposta", description="Agente que fechou o caso")

    def format_task_output(self) -> str:
        """Gera a formatação"""
        protocolos_str = "\n".join([f"- {p}" for p in self.protocolos_sugeridos]) if self.protocolos_sugeridos else "- Nenhum protocolo de emergência ativado no momento."
        return (
            f"RISCO PREVISTO: {self.risco_previsto:.2f}\n\n"
            f"PROTOCOLOS SUGERIDOS:\n"
            f"{protocolos_str}"
        )
