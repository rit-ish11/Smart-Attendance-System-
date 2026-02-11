from backend.db import get_db_connection

def import_parents():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all students
    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()  # list of tuples (id, name)

    for student in students:
        student_id = student[0]
        student_name = student[1]

        # Generate placeholder parent data
        parent_name = f"Parent of {student_name}"
        email = f"parent{student_id}@example.com"
        phone = f"1234567{student_id:03d}"  # dummy phone

        cursor.execute("""
            INSERT INTO parents (student_id, name, email, phone)
            VALUES (%s, %s, %s, %s)
        """, (student_id, parent_name, email, phone))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All parents imported successfully!")

if __name__ == "__main__":
    import_parents()
