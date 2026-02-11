from flask import Blueprint, jsonify

teachers_bp = Blueprint("teachers", __name__)

@teachers_bp.route("/test", methods=["GET"])
def test_teachers():
    return jsonify({"message": "👩‍🏫 Teachers route working"})
