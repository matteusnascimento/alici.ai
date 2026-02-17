from flask import Blueprint, request, jsonify
from services.openai_client import gerar_resposta

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    mensagem = data.get("message")

    if not mensagem:
        return jsonify({"error": "Mensagem vazia"}), 400

    resposta = gerar_resposta(mensagem)

    return jsonify({
        "reply": resposta
    })
