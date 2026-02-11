import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",        # change if you use another user
    password="Ritish@@11"  # enter your MySQL root password
)

cursor = conn.cursor()

# Create database
cursor.execute("CREATE DATABASE IF NOT EXISTS attendance_system;")
cursor.execute("USE attendance_system;")

print("✅ Database created successfully!")

cursor.close()
conn.close()
