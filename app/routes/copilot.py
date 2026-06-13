from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required

from app.services.ai.copilot_service import CopilotService

copilot_bp = Blueprint("copilot", __name__, template_folder="../templates/copilot")

@copilot_bp.route("/")
@login_required
def index():
    return render_template("copilot/index.html")


@copilot_bp.route("/api/context", methods=["GET"])
@login_required
def context():
    service = CopilotService()
    return jsonify(service.get_snapshot())

@copilot_bp.route("/api/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        service = CopilotService()
        result = service.respond(user_message)
        return jsonify(result)
    except Exception:
        return jsonify({"error": "Unable to process Copilot request at the moment."}), 500
