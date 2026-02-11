import cv2
import face_recognition
import pickle
import csv
import os
import datetime
import threading
import time
import speech_recognition as sr

# ==============================
# Load Encodings
# ==============================
print("[INFO] Loading encodings...")
ENCODINGS_PATH = os.path.join(os.path.dirname(__file__), "encodings.pickle")

def load_known_faces():
    with open(ENCODINGS_PATH, "rb") as f:
        data = pickle.load(f)

    encodings = data.get("encodings", [])
    names = data.get("names", [])
    rolls = data.get("rolls", [f"ROLL{i+1}" for i in range(len(names))])
    return encodings, names, rolls

known_encodings, known_names, known_rolls = load_known_faces()

# ==============================
# Attendance CSV
# ==============================
csv_file = "attendance_voice.csv"
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Roll No", "Date", "Time", "Status"])

attendance_set = set()

def mark_attendance(name, roll_no, status="Present"):
    now = datetime.datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    if (roll_no, date) not in attendance_set:
        with open(csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, roll_no, date, time_str, status])
        attendance_set.add((roll_no, date))
        print(f"[ATTENDANCE] {name} ({roll_no}) marked {status} at {time_str}")

# ==============================
# Voice Recognition
# ==============================
r = sr.Recognizer()

def listen_for_present(name, roll_no):
    deadline = time.time() + 5  # only 5 seconds allowed
    with sr.Microphone() as source:
        print(f"[VOICE] Say 'Present' for {name} ({roll_no}) (within 5 sec)...")
        try:
            while time.time() < deadline:
                audio = r.listen(source, timeout=1, phrase_time_limit=2)
                try:
                    text = r.recognize_google(audio).lower()
                    if "present" in text:
                        mark_attendance(name, roll_no, "Present")
                        return
                    else:
                        print("[VOICE] Wrong word, not marked.")
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    print(f"[VOICE ERROR] {e}")
                    break
        except Exception as e:
            print(f"[VOICE ERROR] {e}")

# ==============================
# Video Stream
# ==============================
print("[INFO] Starting video stream...")
vs = cv2.VideoCapture(0)

frame_count = 0
process_every = 3  # process 1 out of 3 frames

while True:
    ret, frame = vs.read()
    if not ret:
        break

    frame_count += 1
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    if frame_count % process_every == 0:
        boxes = face_recognition.face_locations(rgb, model="hog")
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding, box in zip(encodings, boxes):
            matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
            name, roll_no = "Unknown", "----"

            if True in matches:
                match_index = matches.index(True)
                name = known_names[match_index]
                roll_no = known_rolls[match_index]

                # Start 5-sec voice thread
                threading.Thread(target=listen_for_present, args=(name, roll_no)).start()

            # Scale boxes back
            top, right, bottom, left = box
            top *= 2; right *= 2; bottom *= 2; left *= 2

            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, f"{name} ({roll_no})", (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow("Attendance with Voice", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

vs.release()
cv2.destroyAllWindows()
