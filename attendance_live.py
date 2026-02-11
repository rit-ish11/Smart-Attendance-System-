import cv2
import face_recognition
import pickle
import datetime
import sqlite3
import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(__file__)
ENCODINGS_PATH = os.path.join(BASE_DIR, "encodings.pickle")
CSV_PATH = os.path.join(BASE_DIR, "students.csv")
DB_PATH = os.path.join(BASE_DIR, "attendance_system.db")
REPORT_CSV = os.path.join(BASE_DIR, "attendance_report.csv")

# Load encodings
print("[INFO] Loading encodings...")
data = pickle.load(open(ENCODINGS_PATH, "rb"))

# Load student roll_no -> name mapping from CSV
students_df = pd.read_csv(CSV_PATH, dtype={"roll_no": str})
roll_no_to_name = dict(zip(students_df["roll_no"], students_df["name"]))

# Connect to DB
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Ensure attendance table exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT,
    name TEXT,
    timestamp TEXT,
    status TEXT
)
""")

def mark_attendance(roll_no, name):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO attendance (roll_no, name, timestamp, status) VALUES (?, ?, ?, ?)",
                   (roll_no, name, timestamp, "Present"))
    conn.commit()
    print(f"[ATTENDANCE] {name} ({roll_no}) at {timestamp}")

# ✅ Keep track of recognized students
recognized_rolls = set()

# Start webcam
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    boxes = face_recognition.face_locations(rgb)
    encodings = face_recognition.face_encodings(rgb, boxes)
    for encoding, box in zip(encodings, boxes):
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        face_distances = face_recognition.face_distance(data["encodings"], encoding)
        best_match_index = None
        if len(face_distances) > 0:
            best_match_index = face_distances.argmin()
        name, roll_no = "Unknown", "N/A"
        color = (0, 0, 255)  # 🔴 Default RED for Unknown
        if best_match_index is not None and matches[best_match_index]:
            roll_no = data["names"][best_match_index]   # roll_no stored during training
            name = roll_no_to_name.get(roll_no, "Unknown")
            mark_attendance(roll_no, name)
            recognized_rolls.add(roll_no)  # ✅ Save recognized roll_no
            color = (0, 255, 0)  # 🟢 Green for known student
        # Draw bounding box
        (top, right, bottom, left) = box
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, f"{name} ({roll_no})", (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow("Attendance - Press Q to Quit", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

# ✅ Export attendance to CSV with Present/Absent
today = datetime.date.today().strftime("%Y-%m-%d")
attendance_records = []

for _, row in students_df.iterrows():
    roll_no = row["roll_no"]
    name = row["name"]

    if roll_no in recognized_rolls:
        status = "Present"
    else:
        status = "Absent"

    attendance_records.append({
        "name": name,
        "roll_no": roll_no,
        "date": today,
        "status": status
    })

report_df = pd.DataFrame(attendance_records)
report_df.to_csv(REPORT_CSV, index=False)

print(f"[INFO] Attendance exported to {REPORT_CSV}")

conn.close()
