from flask import Blueprint, request, jsonify
from core.brain import brain

api = Blueprint("api", __name__)


@api.route("/chat", methods=["POST"])
def chat():

    data = request.json or {}
    message = data.get("message", "")

    response = brain(message)

    return jsonify({
        "response": response
    })


@api.route("/voice", methods=["POST"])
def voice():

    data = request.json or {}
    text = data.get("text", "")

    response = brain(text)

    return jsonify({
        "response": response
    })
