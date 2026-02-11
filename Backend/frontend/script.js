let selectedUserType = '';

function showLogin(department) {
    document.getElementById('loginSection').style.display = 'block';
    document.getElementById('loginDept').innerText = department + " Login";
}

function showLoginForm(userType) {
    selectedUserType = userType;
    document.getElementById('userTypeSelection').style.display = 'none';
    document.getElementById('loginForms').style.display = 'block';

    // Hide all forms
    document.getElementById('teacherForm').style.display = 'none';
    document.getElementById('studentForm').style.display = 'none';
    document.getElementById('parentForm').style.display = 'none';

    // Show selected form
    if(userType === 'teacher') document.getElementById('teacherForm').style.display = 'block';
    if(userType === 'student') document.getElementById('studentForm').style.display = 'block';
    if(userType === 'parent') document.getElementById('parentForm').style.display = 'block';
}

async function submitLogin(event, userType) {
    event.preventDefault();

    let payload = {};
    let apiUrl = '';

    if(userType === 'teacher') {
        payload = {
            email: document.getElementById('teacherEmail').value,
            password: document.getElementById('teacherPassword').value
        };
        apiUrl = 'http://localhost:5000/api/teachers/login';
    }
    if(userType === 'student') {
        payload = {
            roll_no: document.getElementById('studentRoll').value,
            password: document.getElementById('studentPassword').value
        };
        apiUrl = 'http://localhost:5000/api/students/login';
    }
    if(userType === 'parent') {
        payload = {
            email: document.getElementById('parentEmail').value,
            password: document.getElementById('parentPassword').value
        };
        apiUrl = 'http://localhost:5000/api/parents/login';
    }

    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if(response.ok) {
            alert(`✅ Login Successful: Welcome ${data.name}`);
            // Redirect to dashboard page here if exists
        } else {
            alert(`❌ Login Failed: ${data.message}`);
        }
    } catch(err) {
        console.error(err);
        alert('❌ Error connecting to server');
    }
}
