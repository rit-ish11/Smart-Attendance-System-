# 🎓 Smart Attendance System (Face Recognition Based)

![Project Type](https://img.shields.io/badge/Project-Type%20AI%20%7C%20Web%20App-blue)
![Tech Stack](https://img.shields.io/badge/Tech-Python%20%7C%20Flask%20%7C%20OpenCV-green)
![Status](https://img.shields.io/badge/Status-Completed-success)

---

## 🚀 Project Overview

The Smart Attendance System is a software-based web application that automates attendance recording using real-time face recognition. 

The system uses a phone camera or webcam to detect and recognize student faces. When a registered student is identified, their attendance is automatically recorded and stored in a CSV file. If an unregistered or wrong person appears, the system captures their image and triggers a voice alert.

This project eliminates manual attendance processes and introduces AI-powered automation for improved accuracy and security.

---

## 🎯 Key Features

✔ Real-time face detection and recognition  
✔ Webcam / Phone camera support  
✔ Student dataset creation with image storage  
✔ Automatic attendance recording  
✔ CSV-based attendance report generation  
✔ Voice alert system for unknown faces  
✔ Captures image of unauthorized person  

---

## 🧠 Technologies Used

- Python  
- Flask (Web Framework)  
- HTML & CSS (Frontend)  
- OpenCV  
- face_recognition Library  
- NumPy  
- Pandas  
- Text-to-Speech Library (pyttsx3 or similar)  

---

## ⚙️ Working Principle

1. Student images are captured and stored to create a dataset.
2. Face encodings are generated using the face_recognition library.
3. When the camera starts, the system detects faces in real-time.
4. The detected face is compared with stored encodings.
5. If matched:
   - Attendance is recorded with name and timestamp.
   - Data is saved in a CSV file.
6. If not matched:
   - Image is captured.
   - Voice alert is triggered.
   - Unauthorized attempt is logged.

---

## 📂 Project Structure

Smart-Attendance-System/
│
├── static/
├── templates/
├── dataset/
├── unknown_faces/
├── attendance.csv
├── app.py
└── README.md





---

## 📊 Advantages

- Fully automated system  
- Reduces proxy attendance  
- Real-time monitoring  
- Easy report generation  
- Secure and scalable  

---

## 🌍 Applications

- Schools & Colleges  
- Coaching Centers  
- Offices  
- Training Institutes  

---

## 🔮 Future Enhancements

- Cloud database integration  
- Admin dashboard  
- Mobile app integration  
- Multi-camera support  
- Advanced AI model for higher accuracy  

---

## 👨‍💻 Author

**Ritish**  
B.Tech – Electrical / Electronics Engineering  
Interested in AI, Computer Vision & Automation

