import cv2
import face_recognition
import pickle
import csv
import os
from datetime import datetime
import pandas as pd

# ==============================
# Load encodings
# ==============================
ENCODINGS_PATH = "encodings.pickle"
CSV_PATH = "students.csv"

if not os.path.exists(ENCODINGS_PATH):
    print("Encodings file not found! Please generate encodings first.")
    exit()

with open(ENCODINGS_PATH, "rb") as f:
    data = pickle.load(f)

known_encodings = data["encodings"]
known_rolls = data["names"]   # roll_no stored in "names"

# Load roll_no → name mapping
students_df = pd.read_csv(CSV_PATH, dtype={"roll_no": str})
roll_no_to_name = dict(zip(students_df["roll_no"], students_df["name"]))

# ==============================
# CSV setup
# ==============================
CSV_FILE = "attendance_camera.csv"
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Roll No", "Date", "Time", "Status"])

recognized_rolls = set()
UNKNOWN_DIR = "unknown_faces"
os.makedirs(UNKNOWN_DIR, exist_ok=True)

# ==============================
# Attendance marking
# ==============================
def mark_attendance(roll_no, name, status="Present"):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, roll_no, date_str, time_str, status])
    print(f"[INFO] Attendance marked: {name} ({roll_no}) on {date_str} {time_str} - {status}")

# ==============================
# Camera
# ==============================
cap = cv2.VideoCapture(0)
print("[INFO] Starting camera... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding, face_loc in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.45)
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)

        roll_no = "N/A"
        name = "Unknown"
        color = (0, 0, 255)  # Red for unknown

        if True in matches:
            best_match_index = face_distances.argmin()
            if matches[best_match_index]:
                roll_no = known_rolls[best_match_index]
                name = roll_no_to_name.get(roll_no, "Unknown")
                color = (0, 255, 0)

                if roll_no not in recognized_rolls:
                    mark_attendance(roll_no, name, "Present")
                    recognized_rolls.add(roll_no)
        else:
            # Save unknown face snapshot
            top, right, bottom, left = [v * 4 for v in face_loc]
            unknown_face = frame[top:bottom, left:right]
            if unknown_face.size > 0:
                filename = os.path.join(
                    UNKNOWN_DIR,
                    f"unknown_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                )
                cv2.imwrite(filename, unknown_face)
                print(f"[INFO] Unknown face saved: {filename}")
                mark_attendance("N/A", "Unknown", "Unknown")

        # Draw bounding box + label
        top, right, bottom, left = [v * 4 for v in face_loc]
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, f"{name} ({roll_no})", (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow("Attendance Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
