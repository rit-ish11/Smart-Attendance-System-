from flask import Blueprint, request, jsonify, Response
import cv2
import face_recognition
import numpy as np
from datetime import datetime

attendance_bp = Blueprint('attendance', __name__)

# ----- GLOBALS -----
camera = cv2.VideoCapture(0)  # open webcam
attendance_data = {
    "total": 50,     # you can fetch this dynamically from DB
    "present": 0,
    "absent": 50
}
recognized_today = set()  # store recognized student roll numbers


# ----- VIDEO STREAM -----
def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # encode frame and send to browser
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@attendance_bp.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# ----- MARK ATTENDANCE -----
@attendance_bp.route('/mark', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    image_data = data['image']  # teacher sends snapshot

    # TODO: decode & run face recognition here

    # mock recognized students
    recognized_students = [
        {"name": "Ravi Kumar", "roll_no": "EE101"},
        {"name": "Priya Singh", "roll_no": "EE102"}
    ]

    # update present/absent count
    for student in recognized_students:
        if student["roll_no"] not in recognized_today:
            recognized_today.add(student["roll_no"])
            attendance_data["present"] += 1
            attendance_data["absent"] -= 1

    return jsonify({"recognized": recognized_students})


# ----- ATTENDANCE STATS -----
@attendance_bp.route('/get_attendance_stats', methods=['GET'])
def get_attendance_stats():
    return jsonify(attendance_data)


# ----- SAVE ATTENDANCE -----
@attendance_bp.route('/submit_attendance', methods=['POST'])
def submit_attendance():
    # Example: save attendance to DB
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"status": "success", "message": f"Attendance saved at {now}"})
