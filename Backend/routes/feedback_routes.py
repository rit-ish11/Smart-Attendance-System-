from flask import Blueprint, jsonify

feedback_bp = Blueprint("feedback", __name__)

@feedback_bp.route("/test")
def test_feedback():
    return jsonify({"message": "Feedback routes working ✅"})
