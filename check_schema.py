
import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'instance', 'cardiosense.db')
print(f"Checking DB at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:", tables)
    
    if ('doctors',) in tables:
        cursor.execute("SELECT * FROM doctors")
        print("Doctors:", cursor.fetchall())
    else:
        print("Table 'doctors' not found.")
        
    if ('doctor',) in tables:
        print("Table 'doctor' found! (Singular)")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
