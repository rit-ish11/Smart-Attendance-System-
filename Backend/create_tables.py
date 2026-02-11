import mysql.connector

# --- Connect to MySQL ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",                # change if you use another MySQL user
    password="Ritish@@11",   # put your MySQL root password here
    database="attendance_system"
)

cursor = conn.cursor()

# --- Create tables ---

tables = [

    # Departments table
    """
    CREATE TABLE IF NOT EXISTS departments (
        dept_id INT AUTO_INCREMENT PRIMARY KEY,
        dept_name VARCHAR(50) UNIQUE NOT NULL
    )
    """,

    # Students table
    """
    CREATE TABLE IF NOT EXISTS students (
        student_id INT AUTO_INCREMENT PRIMARY KEY,
        roll_no VARCHAR(20) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        dept_id INT,
        email VARCHAR(100),
        password_hash VARCHAR(255),
        face_encoding TEXT,
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
    )
    """,

    # Teachers table
    """
    CREATE TABLE IF NOT EXISTS teachers (
        teacher_id INT AUTO_INCREMENT PRIMARY KEY,
        emp_id VARCHAR(20) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        dept_id INT,
        email VARCHAR(100),
        password_hash VARCHAR(255),
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
    )
    """,

    # Parents table
    """
    CREATE TABLE IF NOT EXISTS parents (
        parent_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        name VARCHAR(100),
        email VARCHAR(100),
        password_hash VARCHAR(255),
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    """,

    # Attendance table
    """
    CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        date DATE NOT NULL,
        status ENUM('Present', 'Absent') NOT NULL,
        marked_by INT,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (marked_by) REFERENCES teachers(teacher_id)
    )
    """,

    # Unknown faces log
    """
    CREATE TABLE IF NOT EXISTS unknown_faces (
        unknown_id INT AUTO_INCREMENT PRIMARY KEY,
        image_path VARCHAR(255),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,

    # Feedback from students
    """
    CREATE TABLE IF NOT EXISTS feedback (
        feedback_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT,
        teacher_id INT,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
    )
    """
]

# Execute each table creation
for t in tables:
    cursor.execute(t)

print("✅ All tables created successfully inside attendance_system database!")

cursor.close()
conn.close()
