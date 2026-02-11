import csv
from backend.db import get_db_connection

CSV_FILE = 'C:/Users/ritis/OneDrive/Documents/attendance_system/students.csv'

# Mapping department names to IDs
DEPT_MAP = {
    'EE': 1,   # Electrical
    'CSE': 2,  # Computer Science
    'ECE': 3,  # Electronics
    'CE': 4    # Civil
}

def import_students():
    conn = get_db_connection()
    cursor = conn.cursor()

    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['name']
            roll_no = row['roll_no']
            department_name = row['department_id']  # currently all 'EE'
            department_id = DEPT_MAP.get(department_name, 1)  # default to 1 if missing

            # Insert into students table
            cursor.execute("""
                INSERT INTO students (name, roll_no, department_id)
                VALUES (%s, %s, %s)
            """, (name, roll_no, department_id))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All students imported successfully!")

if __name__ == "__main__":
    import_students()
