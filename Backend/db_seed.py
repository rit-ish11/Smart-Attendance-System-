from backend.db import get_db_connection

def seed_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert sample teachers
    cursor.execute("""
    INSERT INTO teachers (name, department, email, password)
    VALUES 
    ('Dr. Sharma', 'Electrical', 'sharma@college.com', 'hashed_password1'),
    ('Prof. Mehta', 'Computer Science', 'mehta@college.com', 'hashed_password2')
    ON DUPLICATE KEY UPDATE email=email
    """)

    # Insert sample students
    cursor.execute("""
    INSERT INTO students (roll_no, name, department, email)
    VALUES 
    ('EE101', 'Ravi Kumar', 'Electrical', 'ravi@students.com'),
    ('EE102', 'Priya Singh', 'Electrical', 'priya@students.com'),
    ('CS201', 'Amit Patel', 'Computer Science', 'amit@students.com')
    ON DUPLICATE KEY UPDATE roll_no=roll_no
    """)

    # Insert sample parents
    cursor.execute("""
    INSERT INTO parents (student_id, name, email, phone)
    VALUES 
    (1, 'Mr. Kumar', 'kumar_parent@home.com', '9876543210'),
    (2, 'Mrs. Singh', 'singh_parent@home.com', '9876501234')
    ON DUPLICATE KEY UPDATE student_id=student_id
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Sample data inserted successfully!")

if __name__ == "__main__":
    seed_data()
