import json
import os
import re
import uuid
from typing import Dict, Any, List, Optional


class LocalAssistantEngine:
    """
    Motor local de diálogo conversacional do CardioIA.
    Espelha a modelagem de Intents, Entities e Dialog Nodes do IBM Watson Assistant,
    garantindo que o assistente funcione de forma autônoma e resiliente.
    """

    def __init__(self, skill_json_path: Optional[str] = None):
        if skill_json_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            skill_json_path = os.path.join(base_dir, "cardioia_watson_assistant.json")

        self.skill_json_path = skill_json_path
        self.skill_data = self._load_skill()
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def _load_skill(self) -> Dict[str, Any]:
        """Carrega a definição da Skill do Watson Assistant em formato JSON."""
        if os.path.exists(self.skill_json_path):
            with open(self.skill_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def create_session(self) -> str:
        """Cria uma nova sessão conversacional com identificador único."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "history": [],
            "context": {"risk_level": "BAIXO_RISCO", "detected_symptoms": [], "vital_signs": {}},
        }
        return session_id

    def extract_entities(self, text: str) -> List[Dict[str, str]]:
        """Extrai entidades clínicas (@sintoma, @sinal_vital, @fator_risco) da mensagem."""
        text_lower = text.lower()
        entities = []
        raw_entities = self.skill_data.get("entities", [])

        for ent_def in raw_entities:
            entity_name = ent_def.get("entity")
            for val_obj in ent_def.get("values", []):
                val_name = val_obj.get("value")
                synonyms = val_obj.get("synonyms", []) + [val_name.replace("_", " ")]

                for syn in synonyms:
                    if syn.lower() in text_lower:
                        entities.append({
                            "entity": entity_name,
                            "value": val_name,
                            "match": syn,
                        })
                        break

        # Extração de padrões numéricos de pressão arterial (ex: 14/9, 140x90, 14 por 9)
        bp_pattern = re.search(r"(\d{2,3})\s*(?:x|\/|por|\-)\s*(\d{2,3})", text_lower)
        if bp_pattern:
            entities.append({
                "entity": "sinal_vital",
                "value": "pressao_arterial",
                "match": bp_pattern.group(0),
                "values": [int(bp_pattern.group(1)), int(bp_pattern.group(2))],
            })

        # Extração de frequência cardíaca (ex: 110 bpm, 85 batimentos)
        hr_pattern = re.search(r"(\d{2,3})\s*(?:bpm|batimentos|bps)", text_lower)
        if hr_pattern:
            entities.append({
                "entity": "sinal_vital",
                "value": "frequencia_cardiaca",
                "match": hr_pattern.group(0),
                "value_num": int(hr_pattern.group(1)),
            })

        return entities

    def detect_intent(self, text: str, entities: List[Dict[str, str]]) -> Dict[str, Any]:
        """Classifica a intenção primária do usuário com base no texto e entidades."""
        text_lower = text.lower().strip()

        # Normalização básica de pontuação para análise de intenção
        clean_text = re.sub(r"[^\w\s]", " ", text_lower)
        clean_words = clean_text.split()

        # 1. Padrões de Emergência Crítica
        emergency_triggers = [
            "infarto", "socorro", "morrendo", "samu", "emergencia", "emergência",
            "dor insuportavel", "dor insuportável", "dor no peito e suor frio",
            "dor no peito e desmaio", "dormencia no braco", "dormência no braço",
            "dor no braço esquerdo", "dor na mandibula", "dor na mandíbula"
        ]
        has_chest_pain = any(e.get("value") == "dor_no_peito" for e in entities)
        has_radiation = any(e.get("value") == "dor_irradiada" for e in entities)

        if (has_chest_pain and has_radiation) or any(t in text_lower for t in emergency_triggers):
            return {"intent": "emergencia_cardiaca", "confidence": 0.98}

        # 2. Saudações
        greetings = ["ola", "olá", "oi", "bom dia", "boa tarde", "boa noite", "iniciar", "comecar", "começar", "hello", "hey", "saudacoes", "saudações"]
        if any(g in text_lower for g in ["bom dia", "boa tarde", "boa noite"]) or any(w in clean_words for w in ["ola", "olá", "oi", "iniciar", "comecar", "começar", "hello", "hey"]):
            return {"intent": "saudacao", "confidence": 0.95}

        # 3. Despedidas
        farewells = ["tchau", "ate logo", "até logo", "obrigado", "obrigada", "valeu", "encerrar", "finalizar", "fim", "adeus"]
        if any(f in text_lower for f in farewells):
            return {"intent": "despedida", "confidence": 0.95}

        # 4. Ajuda e Comandos
        help_words = ["ajuda", "help", "menu", "opcoes", "opções", "como funciona", "o que voce faz", "o que você faz"]
        if any(h in text_lower for h in help_words) and "cardioia" not in text_lower:
            return {"intent": "ajuda", "confidence": 0.92}

        # 5. Sobre o CardioIA
        about_words = ["cardioia", "quem e voce", "quem é você", "sobre o projeto", "sobre o sistema", "o que e o cardioia", "o que é o cardioia"]
        if any(a in text_lower for a in about_words):
            return {"intent": "sobre_cardioia", "confidence": 0.95}

        # 6. Dúvidas e Prevenção
        prevention_words = ["prevenir", "prevencao", "prevenção", "alimentacao", "alimentação", "dieta", "exercicio", "exercício", "habitos", "hábitos", "colesterol", "sal", "evitar infarto"]
        if any(p in text_lower for p in prevention_words):
            return {"intent": "duvidas_prevencao", "confidence": 0.90}

        # 7. Sinais Vitais Numéricos
        if any(e.get("entity") == "sinal_vital" for e in entities) or re.search(r"\b\d{2,3}\s*(?:x|\/|por)\s*\d{2,3}\b", text_lower):
            return {"intent": "informar_dados_vitais", "confidence": 0.93}

        # 8. Relato de Sintomas
        if any(e.get("entity") == "sintoma" for e in entities) or any(w in text_lower for w in ["sinto", "sentindo", "dor", "falta de ar", "cansaco", "cansaço", "inchaco", "inchaço", "palpitacao", "palpitação", "pressao alta", "pressão alta"]):
            return {"intent": "informar_sintomas", "confidence": 0.88}

        # Fallback
        return {"intent": "anything_else", "confidence": 0.40}

    def _get_node_response(self, intent: str, entities: List[Dict[str, str]]) -> str:
        """Localiza a resposta do nó de diálogo correspondente à intenção."""
        dialog_nodes = self.skill_data.get("dialog_nodes", [])

        node_map = {
            "saudacao": "node_welcome",
            "emergencia_cardiaca": "node_emergencia",
            "informar_sintomas": "node_informar_sintomas",
            "informar_dados_vitais": "node_dados_vitais",
            "duvidas_prevencao": "node_prevencao",
            "sobre_cardioia": "node_sobre",
            "ajuda": "node_ajuda",
            "despedida": "node_despedida",
            "anything_else": "node_fallback",
        }

        target_node_id = node_map.get(intent, "node_fallback")

        for node in dialog_nodes:
            if node.get("dialog_node") == target_node_id:
                generic = node.get("output", {}).get("generic", [])
                if generic:
                    values = generic[0].get("values", [])
                    if values:
                        return values[0].get("text", "")

        return "Como posso ajudar na sua saúde cardiológica hoje?"

    def calculate_risk_level(self, intent: str, entities: List[Dict[str, str]], text: str) -> str:
        """Determina o nível de gravidade clínica (BAIXO, MODERADO, ALTO, EMERGÊNCIA)."""
        if intent == "emergencia_cardiaca":
            return "EMERGENCIA"

        symptoms = [e.get("value") for e in entities if e.get("entity") == "sintoma"]

        # Se houver dor no peito com múltiplos sintomas associados
        if "dor_no_peito" in symptoms and len(symptoms) >= 2:
            return "ALTO_RISCO"

        # Verificação de pressão arterial de crise
        bp_matches = [e for e in entities if e.get("value") == "pressao_arterial" and "values" in e]
        for bp in bp_matches:
            sys, dia = bp["values"]
            if sys < 30 and dia < 30:  # formato como 14/9
                sys *= 10
                dia *= 10
            if sys >= 180 or dia >= 110:
                return "ALTO_RISCO"
            if sys >= 140 or dia >= 90:
                return "MODERADO"

        if symptoms:
            return "MODERADO"

        return "BAIXO_RISCO"

    def process_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Processa a mensagem do usuário e gera a resposta contextualizada,
        metadados de NLU e nível de triagem de risco.
        """
        if not session_id or session_id not in self.sessions:
            session_id = self.create_session()

        entities = self.extract_entities(message)
        intent_data = self.detect_intent(message, entities)
        intent = intent_data["intent"]
        confidence = intent_data["confidence"]
        response_text = self._get_node_response(intent, entities)
        risk_level = self.calculate_risk_level(intent, entities, message)

        session_record = self.sessions[session_id]
        session_record["context"]["risk_level"] = risk_level
        session_record["history"].append({"role": "user", "text": message})
        session_record["history"].append({"role": "assistant", "text": response_text})

        return {
            "response": response_text,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "risk_level": risk_level,
            "session_id": session_id,
            "engine": "local_resilient_engine",
        }
