import cv2, face_recognition, pickle, datetime, sqlite3, pandas as pd
import speech_recognition as sr
import librosa, numpy as np
from scipy.spatial.distance import cosine

# Paths
ENCODINGS_PATH = "encodings.pickle"
CSV_PATH = "students.csv"
DB_PATH = "attendance_system.db"
VOICE_PATH = "voice_profiles.pickle"
REPORT_CSV = "attendance_voice_report.csv"

# Load face encodings
data = pickle.load(open(ENCODINGS_PATH, "rb"))

# Load student mapping
students_df = pd.read_csv(CSV_PATH, dtype={"roll_no": str})
roll_no_to_name = dict(zip(students_df["roll_no"], students_df["name"]))

# Load voice profiles
voice_profiles = pickle.load(open(VOICE_PATH, "rb"))

# DB setup
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance_voice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT,
    name TEXT,
    timestamp TEXT,
    status TEXT
)
""")

def extract_mfcc_from_audio(audio, sr):
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)
    return np.mean(mfcc.T, axis=0)

def verify_voice(roll_no):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎤 Say 'present'...")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=5)

    try:
        text = recognizer.recognize_google(audio).lower()
        print("🗣️ You said:", text)
        if "present" not in text:
            return False

        # Convert audio to numpy
        wav_data = np.frombuffer(audio.get_raw_data(), np.int16).astype(np.float32) / 32768.0
        sr_rate = audio.sample_rate
        features = extract_mfcc_from_audio(wav_data, sr_rate)

        if roll_no in voice_profiles:
            stored_feat = np.array(voice_profiles[roll_no]["features"])
            similarity = 1 - cosine(features, stored_feat)
            print(f"🔍 Voice similarity: {similarity:.2f}")

            return similarity > 0.75  # Threshold

    except Exception as e:
        print("❌ Voice error:", e)
        return False

    return False

def mark_attendance(roll_no, name):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO attendance_voice (roll_no, name, timestamp, status) VALUES (?, ?, ?, ?)",
                   (roll_no, name, timestamp, "Present"))
    conn.commit()
    print(f"[ATTENDANCE] {name} ({roll_no}) at {timestamp}")

# --- Start webcam ---
cap = cv2.VideoCapture(0)
recognized_rolls = set()

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
        color = (0, 0, 255)

        if best_match_index is not None and matches[best_match_index]:
            roll_no = data["names"][best_match_index]
            name = roll_no_to_name.get(roll_no, "Unknown")

            # Voice verification
            if verify_voice(roll_no):
                mark_attendance(roll_no, name)
                recognized_rolls.add(roll_no)
                color = (0, 255, 0)

        # Draw box
        (top, right, bottom, left) = box
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, f"{name} ({roll_no})", (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow("Attendance Voice", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

# Save report
today = datetime.date.today().strftime("%Y-%m-%d")
attendance_records = []
for _, row in students_df.iterrows():
    roll_no = row["roll_no"]
    name = row["name"]
    status = "Present" if roll_no in recognized_rolls else "Absent"
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
