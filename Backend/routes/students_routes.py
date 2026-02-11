from flask import Blueprint, jsonify

students_bp = Blueprint("students", __name__)

@students_bp.route("/test", methods=["GET"])
def test_students():
    return jsonify({"message": "🎓 Students route working"})
