import cv2
import face_recognition
import pickle
import datetime
import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog

# Paths
BASE_DIR = os.path.dirname(__file__)
ENCODINGS_PATH = os.path.join(BASE_DIR, "encodings.pickle")
CSV_PATH = os.path.join(BASE_DIR, "students.csv")
REPORT_CSV = os.path.join(BASE_DIR, "attendance_report.csv")

# Load encodings
print("[INFO] Loading encodings...")
data = pickle.load(open(ENCODINGS_PATH, "rb"))

# Load student roll_no -> name mapping
students_df = pd.read_csv(CSV_PATH, dtype={"roll_no": str})
roll_no_to_name = dict(zip(students_df["roll_no"], students_df["name"]))

recognized_rolls = set()

def mark_attendance(roll_no, name):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[ATTENDANCE] {name} ({roll_no}) at {timestamp}")
    recognized_rolls.add(roll_no)

def process_frame(frame):
    # ✅ Resize for speed (half size)
    frame_small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb = cv2.cvtColor(frame_small, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb, model="hog")  # faster
    encodings = face_recognition.face_encodings(rgb, boxes, model="small")  # ✅ faster small model

    for encoding, box in zip(encodings, boxes):
        matches = face_recognition.compare_faces(data["encodings"], encoding, tolerance=0.5)
        face_distances = face_recognition.face_distance(data["encodings"], encoding)

        best_match_index = None
        if len(face_distances) > 0:
            best_match_index = face_distances.argmin()

        name, roll_no = "Unknown", "N/A"
        color = (0, 0, 255)  # Red for unknown
        if best_match_index is not None and matches[best_match_index]:
            roll_no = data["names"][best_match_index]
            name = roll_no_to_name.get(roll_no, "Unknown")
            mark_attendance(roll_no, name)
            color = (0, 255, 0)  # Green for known

        # Scale back box since image was resized
        top, right, bottom, left = [v * 2 for v in box]
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, f"{name} ({roll_no})", (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow("Result", frame)
    cv2.waitKey(2000)  # ✅ auto-close in 2 seconds
    cv2.destroyAllWindows()

def capture_from_camera():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if ret:
        process_frame(frame)

def capture_from_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title="Select an image",
                                           filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        frame = cv2.imread(file_path)
        process_frame(frame)

# Menu
print("Choose an option:")
print("1. Capture from Camera")
print("2. Upload Image File")
choice = input("Enter choice (1/2): ")

if choice == "1":
    capture_from_camera()
elif choice == "2":
    capture_from_file()
else:
    print("Invalid choice")

# ✅ Export attendance
today = datetime.date.today().strftime("%Y-%m-%d")
attendance_records = []
for _, row in students_df.iterrows():
    roll_no = row["roll_no"]
    name = row["name"]
    status = "Present" if roll_no in recognized_rolls else "Absent"
    attendance_records.append({"name": name, "roll_no": roll_no, "date": today, "status": status})

report_df = pd.DataFrame(attendance_records)
report_df.to_csv(REPORT_CSV, index=False)
print(f"[INFO] Attendance exported to {REPORT_CSV}")
