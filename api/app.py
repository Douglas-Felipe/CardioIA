import os
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from chatbot.watson_client import WatsonAssistantClient
from infrastructure.repositories import FileDataRepository
from infrastructure.nlp_service import TfidfNlpService
from core.use_cases import DiagnosePatientUseCase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CardioIA-App")


def create_app() -> Flask:
    """Factory para criação e configuração da aplicação Flask."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")
    react_dist_dir = os.path.abspath(os.path.join(base_dir, "..", "frontend", "dist"))

    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    CORS(app)

    # Inicializa o cliente conversacional
    watson_client = WatsonAssistantClient()

    # Inicializa o caso de uso de diagnóstico por NLP (Ontologia CardioIA)
    relatos_path = os.path.join(base_dir, "data", "relatos.txt")
    ontologia_path = os.path.join(base_dir, "data", "ontologia.csv")
    use_case = None
    if os.path.exists(ontologia_path):
        try:
            repo = FileDataRepository(relatos_path, ontologia_path)
            nlp_service = TfidfNlpService()
            use_case = DiagnosePatientUseCase(repo, nlp_service)
        except Exception as e:
            logger.warning(f"DiagnosePatientUseCase não inicializado: {e}")

    @app.route("/")
    def index():
        """Renderiza a interface web do assistente conversacional."""
        # Se o build do React existir em frontend/dist, pode servir diretamente o React ou o template
        return render_template("index.html")

    @app.route("/react")
    @app.route("/react/<path:path>")
    def serve_react(path=""):
        """Serve a aplicação React (SPA)."""
        if os.path.exists(react_dist_dir):
            if path != "" and os.path.exists(os.path.join(react_dist_dir, path)):
                return send_from_directory(react_dist_dir, path)
            return send_from_directory(react_dist_dir, "index.html")
        return "React build não encontrado. Execute 'npm run build' na pasta frontend.", 404

    @app.route("/api/chat", methods=["POST"])
    def chat():
        """Endpoint principal para troca de mensagens com o assistente."""
        data = request.get_json(silent=True) or {}
        message = data.get("message", "").strip()
        session_id = data.get("session_id")

        if not message:
            return jsonify({"error": "O campo 'message' é obrigatório."}), 400

        result = watson_client.send_message(message, session_id=session_id)
        return jsonify(result), 200

    @app.route("/api/session", methods=["POST"])
    def new_session():
        """Cria uma nova sessão de atendimento conversacional."""
        session_id = watson_client.create_session()
        return jsonify({"session_id": session_id}), 201

    @app.route("/api/health", methods=["GET"])
    def health():
        """Verifica a integridade do backend e da conexão com o Watson."""
        return jsonify({
            "status": "healthy",
            "watson_connected": watson_client.is_watson_available(),
            "engine": "ibm_watson" if watson_client.is_watson_available() else "local_resilient",
            "version": "1.0.0",
        }), 200

    @app.route("/api/triage", methods=["POST"])
    def triage():
        """
        Executa triagem integrada do relato do paciente cruzando
        com a ontologia de patologias cardiológicas e o classificador.
        """
        data = request.get_json(silent=True) or {}
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "O campo 'text' é obrigatório."}), 400

        chat_result = watson_client.send_message(text)

        disease_suggestion = "Em avaliação clínica"
        similarity_confidence = 0.0

        if use_case:
            try:
                diseases = use_case._repository.get_diseases_ontology()
                if diseases:
                    disease_texts = [d.symptoms_text for d in diseases]
                    use_case._nlp_service.train(disease_texts)
                    best_idx, conf = use_case._nlp_service.find_most_similar(text)
                    if conf > 0.05:
                        disease_suggestion = diseases[best_idx].name
                        similarity_confidence = conf
            except Exception as e:
                logger.warning(f"Erro ao consultar ontologia: {e}")

        return jsonify({
            "relato": text,
            "triagem_chatbot": chat_result,
            "sugestao_ontologia": disease_suggestion,
            "confianca_ontologia": similarity_confidence,
        }), 200

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"🫀 Servidor CardioIA Chatbot rodando em http://{host}:{port}")
    app.run(host=host, port=port, debug=True)
