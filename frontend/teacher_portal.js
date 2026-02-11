// Access the camera
const video = document.getElementById('video');

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Error accessing camera:", err);
        alert("❌ Unable to access camera");
    });

// Capture image and send to backend
function captureImage() {
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/jpeg');

    fetch('http://localhost:5000/api/attendance/mark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData })
    })
    .then(res => res.json())
    .then(data => {
        displayRecognized(data);
    })
    .catch(err => {
        console.error(err);
        alert("❌ Error sending image to server");
    });
}

// Display recognized faces
function displayRecognized(data) {
    const container = document.getElementById('recognizedFaces');
    container.innerHTML = '<h3>Recognized Students</h3>'; // reset

    data.recognized.forEach(student => {
        const div = document.createElement('div');
        div.classList.add('student-box');
        div.innerText = `${student.name} (${student.roll_no.slice(-3)})`;
        container.appendChild(div);
    });
}

// Voice recognition placeholder
function startVoiceRecognition() {
    alert("Voice attendance will be implemented later");
}
