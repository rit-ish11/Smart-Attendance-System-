from flask import Blueprint, jsonify

parents_bp = Blueprint("parents", __name__)

@parents_bp.route("/test", methods=["GET"])
def test_parents():
    return jsonify({"message": "👨‍👩‍👦 Parents route working"})
