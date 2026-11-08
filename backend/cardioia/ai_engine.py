"""Motor de IA integrado: Pipeline Multiagente + ML da Fase 6 e LLM opcional.

Fluxo para cada leitura de telemetria:
  1. Regras clínicas determinísticas (mesma lógica do edge MicroPython)
  2. Montagem das 10 features do modelo da Fase 6 (4 dos sensores + 6 fixas)
  3. Pipeline multiagente Hub-and-Spoke (Orquestrador -> Analista de Risco [ML]
     -> Especialista em Protocolos -> Planejador de Resposta)
  4. Consolidação do nível de risco + mensagens para médico e paciente
  5. (Opcional, assíncrono) LLM reescreve a recomendação em linguagem natural
"""

import logging
import threading
from typing import Any, Dict, List, Optional, Tuple

from . import llm
from . import paths  # noqa: F401 - registra fase_6/ e api/ no sys.path
from .config import settings
from .vitals_rules import ATENCAO, CRITICO, NORMAL, evaluate_vitals, worst

logger = logging.getLogger("cardioia.ai_engine")

ML_TO_LEVEL = {"ALTO RISCO": CRITICO, "RISCO MODERADO": ATENCAO, "BAIXO RISCO": NORMAL}

PATIENT_MESSAGES = {
    NORMAL: "Seus sinais estão dentro do esperado. Continue com sua rotina e hidrate-se.",
    ATENCAO: "Alguns sinais merecem atenção. Fique em repouso; a equipe médica está acompanhando.",
    CRITICO: "Sinais de alerta detectados! A equipe médica foi notificada. "
    "Se sentir dor no peito ou falta de ar, ligue 192 (SAMU).",
}


class AIEngine:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._runner = None
        self.ml_available = False
        self.ml_error: Optional[str] = None
        self._llm_cache: Dict[Tuple, Optional[str]] = {}
        self._llm_pending: set = set()
        self._init_fase6()

    # ------------------------------------------------------------------ setup
    def _init_fase6(self) -> None:
        try:
            from src.config import MODEL_PIPELINE_PATH  # fase_6

            if not MODEL_PIPELINE_PATH.exists():
                logger.info("Modelo da Fase 6 não encontrado; treinando pipeline (primeira execução)...")
                from src.ml.train import run_training_pipeline

                run_training_pipeline()

            from src.agents.runner import MultiAgentPipelineRunner

            self._runner = MultiAgentPipelineRunner()
            self.ml_available = True
            logger.info("Pipeline multiagente da Fase 6 carregado (%s).", MODEL_PIPELINE_PATH.name)
        except Exception as exc:  # noqa: BLE001
            self.ml_error = str(exc)
            logger.exception("Pipeline da Fase 6 indisponível; operando apenas com regras clínicas.")

    # --------------------------------------------------------------- helpers
    @staticmethod
    def build_features(bpm: float, spo2: float, temperature: float, systolic: float) -> Dict[str, float]:
        features = dict(settings.fixed_features)
        features.update(
            {
                "fc_media": float(bpm),
                "spo2_media": float(spo2),
                "temperatura": float(temperature),
                "pa_sistolica": float(systolic),
            }
        )
        return features

    def _run_multiagent(self, features: Dict[str, float]) -> Dict[str, Any]:
        with self._lock:
            final = self._runner.run(features)
            trace = [
                {"de": m.sender, "para": m.recipient, "tipo": m.message_type, "conteudo": str(m.content)}
                for m in self._runner.history
            ]
        return {
            "probabilidade": float(final.risco_previsto),
            "classificacao": final.classificacao,
            "protocolos": list(final.protocolos_sugeridos),
            "plano_contingencia": final.plano_contingencia,
            "agente_emissor": final.agente_emissor,
            "trace": trace,
        }

    def _schedule_llm(self, key: Tuple, prompt: str) -> None:
        if llm.provider_name() == "none" or key in self._llm_cache or key in self._llm_pending:
            return
        self._llm_pending.add(key)

        def worker() -> None:
            try:
                self._llm_cache[key] = llm.summarize(prompt)
            finally:
                self._llm_pending.discard(key)

        threading.Thread(target=worker, daemon=True).start()

    # ------------------------------------------------------------------- API
    def analyze(self, bpm: float, spo2: float, temperature: float, systolic: float) -> Dict[str, Any]:
        status_sinais, per_signal, alerts = evaluate_vitals(bpm, spo2, temperature, systolic)
        features = self.build_features(bpm, spo2, temperature, systolic)

        ml: Optional[Dict[str, Any]] = None
        if self.ml_available:
            try:
                ml = self._run_multiagent(features)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Falha no pipeline multiagente: %s", exc)

        ml_level = ML_TO_LEVEL.get(ml["classificacao"], NORMAL) if ml else NORMAL
        nivel = worst(status_sinais, ml_level)

        protocolos: List[str] = ml["protocolos"] if ml else []
        recomendacao = self._deterministic_recommendation(nivel, alerts, ml)

        key = (nivel, ml["classificacao"] if ml else None, tuple(alerts), tuple(protocolos))
        linhas = [
            f"Sinais: FC={bpm:.0f} bpm, SpO2={spo2:.0f}%, Temp={temperature:.1f} °C, PA sistólica={systolic:.0f} mmHg.",
            f"Alertas: {', '.join(alerts) or 'nenhum'}.",
        ]
        if ml:
            linhas.append(f"Risco ML (Fase 6): {ml['probabilidade']:.2f} ({ml['classificacao']}).")
        linhas.append(f"Protocolos: {', '.join(protocolos) or 'nenhum'}.")
        linhas.append(f"Nível consolidado: {nivel}.")
        prompt = "\n".join(linhas)
        self._schedule_llm(key, prompt)

        return {
            "nivel": nivel,
            "status_sinais": status_sinais,
            "status_por_sinal": per_signal,
            "alertas": alerts,
            "ml": ml,
            "features_modelo": features,
            "protocolos": protocolos,
            "recomendacao": recomendacao,
            "resumo_ia": self._llm_cache.get(key),
            "llm_provider": llm.provider_name(),
            "mensagem_paciente": PATIENT_MESSAGES[nivel],
        }

    @staticmethod
    def _deterministic_recommendation(nivel: str, alerts: List[str], ml: Optional[Dict[str, Any]]) -> str:
        partes = []
        if ml:
            partes.append(f"Modelo preditivo da Fase 6: probabilidade de pico de risco {ml['probabilidade']:.0%} ({ml['classificacao']}).")
        if alerts:
            partes.append("Alterações: " + "; ".join(alerts) + ".")
        if ml and ml.get("plano_contingencia"):
            partes.append(ml["plano_contingencia"])
        elif nivel == CRITICO:
            partes.append("Acionar equipe médica imediatamente e reavaliar o paciente à beira-leito.")
        elif nivel == ATENCAO:
            partes.append("Intensificar monitorização e reavaliar em 15 minutos.")
        else:
            partes.append("Manter monitorização de rotina.")
        return " ".join(partes)


_engine: Optional[AIEngine] = None


def get_engine() -> AIEngine:
    global _engine
    if _engine is None:
        _engine = AIEngine()
    return _engine
