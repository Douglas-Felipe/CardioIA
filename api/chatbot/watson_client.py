import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from .local_assistant_engine import LocalAssistantEngine

# Carrega variáveis de ambiente do arquivo .env caso exista
load_dotenv()

logger = logging.getLogger(__name__)


class WatsonAssistantClient:
    """
    Cliente para integração com a API do IBM Watson Assistant (V2 / V1).
    Possui fallback automático para o LocalAssistantEngine caso as credenciais
    não estejam configuradas ou o serviço esteja inacessível.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        service_url: Optional[str] = None,
        assistant_id: Optional[str] = None,
        version: str = "2021-06-14",
    ):
        self.api_key = api_key or os.getenv("WATSON_API_KEY")
        self.service_url = service_url or os.getenv("WATSON_SERVICE_URL")
        self.assistant_id = assistant_id or os.getenv("WATSON_ASSISTANT_ID")
        self.version = version or os.getenv("WATSON_VERSION", "2021-06-14")

        self.local_engine = LocalAssistantEngine()
        self.watson_service = None
        self._initialize_watson()

    def _initialize_watson(self) -> None:
        """Tenta inicializar o SDK do IBM Watson se as credenciais forem válidas."""
        if self.api_key and self.service_url and self.assistant_id:
            try:
                from ibm_watson import AssistantV2
                from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

                authenticator = IAMAuthenticator(self.api_key)
                assistant = AssistantV2(
                    version=self.version, authenticator=authenticator
                )
                assistant.set_service_url(self.service_url)
                self.watson_service = assistant
                logger.info("IBM Watson Assistant conectado com sucesso via IBM Cloud SDK.")
            except Exception as e:
                logger.warning(f"Falha ao instanciar IBM Watson Assistant: {e}. Usando motor local resiliente.")
                self.watson_service = None
        else:
            logger.info("Credenciais do IBM Watson não configuradas. Operando com motor local de diálogo.")
            self.watson_service = None

    def is_watson_available(self) -> bool:
        """Indica se a conexão real com a nuvem da IBM está ativa."""
        return self.watson_service is not None

    def create_session(self) -> str:
        """Cria uma sessão no Watson Assistant ou no motor local."""
        if self.watson_service and self.assistant_id:
            try:
                response = self.watson_service.create_session(
                    assistant_id=self.assistant_id
                ).get_result()
                return response.get("session_id", "")
            except Exception as e:
                logger.warning(f"Erro ao criar sessão no Watson Assistant: {e}. Criando sessão local.")

        return self.local_engine.create_session()

    def send_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Envia uma mensagem para o Watson Assistant.
        Em caso de ausência de credenciais ou indisponibilidade, recorre ao motor local.
        """
        if self.watson_service and self.assistant_id and session_id:
            try:
                response = self.watson_service.message(
                    assistant_id=self.assistant_id,
                    session_id=session_id,
                    input={"message_type": "text", "text": message},
                ).get_result()

                output = response.get("output", {})
                generic = output.get("generic", [])
                response_texts = []
                for item in generic:
                    if item.get("response_type") == "text":
                        response_texts.append(item.get("text", ""))

                combined_text = "\n\n".join(response_texts) if response_texts else "Olá, como posso ajudar com sua saúde cardiológica?"

                intents = output.get("intents", [])
                primary_intent = intents[0].get("intent", "anything_else") if intents else "anything_else"
                confidence = intents[0].get("confidence", 0.0) if intents else 0.0

                entities = [
                    {"entity": e.get("entity"), "value": e.get("value"), "match": e.get("value")}
                    for e in output.get("entities", [])
                ]

                risk_level = self.local_engine.calculate_risk_level(primary_intent, entities, message)

                return {
                    "response": combined_text,
                    "intent": primary_intent,
                    "confidence": confidence,
                    "entities": entities,
                    "risk_level": risk_level,
                    "session_id": session_id,
                    "engine": "ibm_watson_assistant_v2",
                }
            except Exception as e:
                logger.warning(f"Erro na chamada da API do Watson: {e}. Executando fallback local.")

        # Executa motor local resiliente
        return self.local_engine.process_message(message, session_id=session_id)
