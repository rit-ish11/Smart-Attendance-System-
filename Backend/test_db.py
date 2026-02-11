from backend.db import get_db_connection

conn = get_db_connection()
if conn:
    print("✅ Database connection successful!")
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    print("📂 Tables:", cursor.fetchall())
    conn.close()
else:
    print("❌ Failed to connect.")
