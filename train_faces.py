import os
import cv2
import face_recognition
import pickle

# Path to dataset (students images stored in roll_no folders)
dataset_path = "dataset"

# Path to save encodings inside backend folder
encodings_path = os.path.join("backend", "encodings.pickle")

known_encodings = []
known_names = []

# Loop over each student's folder
for student_id in os.listdir(dataset_path):
    student_folder = os.path.join(dataset_path, student_id)

    if not os.path.isdir(student_folder):
        continue

    # Loop over each image of the student
    for image_name in os.listdir(student_folder):
        image_path = os.path.join(student_folder, image_name)

        image = cv2.imread(image_path)
        if image is None:
            continue

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect face locations
        boxes = face_recognition.face_locations(rgb, model="hog")

        # Encode faces
        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            known_encodings.append(encoding)
            known_names.append(student_id)  # use roll_no (folder name)

# Save encodings to backend/encodings.pickle
data = {"encodings": known_encodings, "names": known_names}
with open(encodings_path, "wb") as f:
    pickle.dump(data, f)

print(f"[INFO] Encodings saved to {encodings_path}")
