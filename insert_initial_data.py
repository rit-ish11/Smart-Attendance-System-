import mysql.connector

# --- Connect to MySQL ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",                # change if needed
    password="Ritish@@11",   # your MySQL root password
    database="attendance_system"
)

cursor = conn.cursor()

# Insert Departments (only if empty)
departments = ["Electrical Engineering (EE)", "Computer Science (CSE)", "Electronics & Communication (ECE)", "Civil Engineering (CE)"]

for dept in departments:
    cursor.execute("SELECT * FROM departments WHERE dept_name = %s", (dept,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO departments (dept_name) VALUES (%s)", (dept,))

# Insert a sample Teacher
cursor.execute("SELECT * FROM teachers WHERE emp_id = 'T001'")
if cursor.fetchone() is None:
    cursor.execute("""
        INSERT INTO teachers (emp_id, name, dept_id, email, password_hash)
        VALUES ('T001', 'Prof. Sharma', 1, 'sharma@abvgiet.ac.in', 'hashed_password_here')
    """)

# Insert a sample Student
cursor.execute("SELECT * FROM students WHERE roll_no = 'EE001'")
if cursor.fetchone() is None:
    cursor.execute("""
        INSERT INTO students (roll_no, name, dept_id, email, password_hash)
        VALUES ('EE001', 'Abhay Kumar', 1, 'abhay@student.ac.in', 'hashed_password_here')
    """)

conn.commit()
print("✅ Default departments + sample teacher + sample student inserted!")

cursor.close()
conn.close()
