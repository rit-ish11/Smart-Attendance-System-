from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import sqlite3
import os
import os
import pickle
import cv2
import face_recognition
import numpy as np
from datetime import datetime

app = Flask(__name__)

# ---------------------- DATABASE SETUP ----------------------
DB_NAME = "attendance_system.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Teachers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_name TEXT NOT NULL,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT,
            status TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()

# Initialize database
init_db()

# ---------------------- HELPER: Load known students ----------------------
def load_known_faces():
    import os
    import pickle
    import pandas as pd

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ENCODINGS_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "encodings.pickle"))


    CSV_PATH = "students.csv"

    # Load encodings
    data = pickle.load(open(ENCODINGS_PATH, "rb"))

    # Load roll_no -> name mapping
    students_df = pd.read_csv(CSV_PATH, dtype={"roll_no": str})
    roll_no_to_name = dict(zip(students_df["roll_no"], students_df["name"]))

    encodings, ids, names, rolls = [], [], [], []
    for roll_no in data["names"]:  # names in pickle = roll_no
        if roll_no in roll_no_to_name:
            idx = list(data["names"]).index(roll_no)
            encodings.append(data["encodings"][idx])
            ids.append(roll_no)  # use roll_no as ID
            names.append(roll_no_to_name[roll_no])
            rolls.append(roll_no)
    return encodings, ids, names, rolls

# ✅ Load global known data ONCE
known_encodings, known_ids, known_names, known_rolls = load_known_faces()
attendance_today = set()

# ---------------------- HOME ----------------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------------- REGISTER ----------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        role = request.form.get("role")
        name = request.form.get("name")
        roll_no = request.form.get("roll_no")
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        try:
            if role == "student":
                cursor.execute(
                    "INSERT INTO students (name, roll_no, username, password) VALUES (?, ?, ?, ?)",
                    (name, roll_no, username, password)
                )
                conn.commit()
                message = f"✅ Student {name} (Roll {roll_no}) registered!"
            elif role == "teacher":
                cursor.execute(
                    "INSERT INTO teachers (teacher_name, username, password) VALUES (?, ?, ?)",
                    (name, username, password)
                )
                conn.commit()
                message = f"✅ Teacher {name} registered!"
            else:
                message = "❌ Invalid role!"
        except sqlite3.IntegrityError:
            message = "⚠️ Username or Roll already exists!"
        finally:
            conn.close()

        return message

    return render_template("register.html")

# ---------------------- LOGIN ----------------------
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE username=? AND password=?", (username, password))
    student = cursor.fetchone()
    if student:
        conn.close()
        return f"✅ Logged in as Student: {student[1]} (Roll: {student[2]})"

    cursor.execute("SELECT * FROM teachers WHERE username=? AND password=?", (username, password))
    teacher = cursor.fetchone()
    conn.close()
    if teacher:
        return render_template("teacher_dashboard.html", teacher_name=teacher[1])

    return "❌ Invalid username or password!"

# ---------------------- TEACHER LOGIN ----------------------
@app.route("/teacher_login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        teacher_name = request.form.get("teacher_name")
        password = request.form.get("password")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teachers WHERE teacher_name=? AND password=?", (teacher_name, password))
        teacher = cursor.fetchone()
        conn.close()

        if teacher:
            return render_template("teacher_dashboard.html", teacher_name=teacher_name)

        return "❌ Invalid teacher login!"
    return render_template("teacher_login.html")

# ---------------------- TEACHER TAKE ATTENDANCE PAGE ----------------------
@app.route("/take_attendance")
def take_attendance():
    return render_template("attendance_capture.html")

# ---------------------- LIVE ATTENDANCE ----------------------
@app.route("/attendance_live")
def attendance_live():
    return render_template("attendance_live.html")

@app.route("/video_feed")
def video_feed():
    return Response(gen_live_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

def gen_live_frames():
    camera = cv2.VideoCapture(0)
    unknown_dir = "static/unknowns"
    os.makedirs(unknown_dir, exist_ok=True)

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(rgb)
            encs = face_recognition.face_encodings(rgb, faces)

            for encoding, (top, right, bottom, left) in zip(encs, faces):
                face_distances = face_recognition.face_distance(known_encodings, encoding)
                best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None

                name, roll, sid = "Unknown", "???", None
                if best_match_index is not None and face_distances[best_match_index] < 0.5:
                    sid, name, roll = known_ids[best_match_index], known_names[best_match_index], known_rolls[best_match_index]
                    attendance_today.add(sid)

                    # ✅ Green box for known
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, f"{name} ({roll})", (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    # ❌ Red box + save unknown face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(frame, "Unknown", (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    # Crop and save face
                    face_img = frame[top:bottom, left:right]
                    if face_img.size > 0:  # avoid empty crops
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
                        filename = os.path.join(unknown_dir, f"unknown_{timestamp}.jpg")
                        cv2.imwrite(filename, face_img)
                        print(f"[📸 Unknown saved] {filename}")

            # Stream frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ---------------------- ATTENDANCE STATS ----------------------
@app.route("/get_attendance_stats")
def get_attendance_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Present'", (today,))
    present = cursor.fetchone()[0]

    absent = total - present
    conn.close()

    return jsonify({"total": total, "present": present, "absent": absent})

@app.route("/submit_attendance", methods=["POST"])
def submit_attendance():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Mark absentees (those not in present list)
    cursor.execute("SELECT id FROM students")
    all_students = [row[0] for row in cursor.fetchall()]

    for sid in all_students:
        cursor.execute("SELECT * FROM attendance WHERE student_id=? AND date=?", (sid, today))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)",
                           (sid, today, "Absent"))

    conn.commit()
    conn.close()

    return jsonify({"message": "Attendance saved successfully!"})

# ---------------------- CAPTURE & RECOGNIZE ----------------------
@app.route("/capture_photo")
def capture_photo():
    print("📸 /capture_photo route triggered!")  # Debug log
    try:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("❌ Camera could not be opened")
            return "Error: Could not access the camera", 500

        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            print("❌ Failed to capture frame")
            return "Error: Failed to capture image", 500

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)
        encs = face_recognition.face_encodings(rgb, faces)

        if len(faces) == 0:
            print("⚠️ No face detected")
            return "No face detected. Please try again.", 200

        present_ids = []
        for encoding, (top, right, bottom, left) in zip(encs, faces):
            face_distances = face_recognition.face_distance(known_encodings, encoding)
            best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None

            name, roll, sid = "Unknown", "???", None
            if best_match_index is not None and face_distances[best_match_index] < 0.5:
                sid, name, roll = known_ids[best_match_index], known_names[best_match_index], known_rolls[best_match_index]
                attendance_today.add(sid)
                present_ids.append(sid)

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"{name} ({roll[-3:]})", (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                # Mark red for unknown
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_path = f"static/captured_{timestamp}.jpg"
        cv2.imwrite(saved_path, frame)

        total_students = len(known_ids)
        present_count = len(set(present_ids))
        absent_count = total_students - present_count

        print(f"✅ Attendance captured: Present={present_count}, Absent={absent_count}")

        return render_template("attendance_photo.html",
                               image_path=saved_path,
                               present=present_count,
                               absent=absent_count)

    except Exception as e:
        print("🔥 ERROR in /capture_photo:", e)
        return f"Unexpected error: {e}", 500

# ---------------------- MAIN ----------------------
if __name__ == "__main__":
    app.run(debug=True)
