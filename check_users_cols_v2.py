
import sqlite3
conn = sqlite3.connect('bizsight.db')
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(users);")
cols = [row[1] for row in cursor.fetchall()]
print(f"Columns: {cols}")
conn.close()
