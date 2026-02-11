from flask import Blueprint, request, jsonify
from ..config import get_db_connection
import bcrypt

auth_bp = Blueprint("auth", __name__)

# --- Teacher Login ---
@auth_bp.route("/teacher_login", methods=["POST"])
def teacher_login():
    data = request.json
    emp_id = data.get("emp_id")
    password = data.get("password")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM teachers WHERE emp_id=%s", (emp_id,))
    teacher = cursor.fetchone()

    if teacher and bcrypt.checkpw(password.encode("utf-8"), teacher["password_hash"].encode("utf-8")):
        return jsonify({"status": "success", "message": "Login successful", "teacher": teacher})
    else:
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401
