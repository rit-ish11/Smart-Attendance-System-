import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",       # change if your MySQL user is different
            password="Ritish@@11",  # 🔴 put your MySQL password here
            database="smart_attendance"
        )
        return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None
