
import sqlite3
conn = sqlite3.connect('bizsight.db')
cursor = conn.cursor()
cursor.execute("SELECT username FROM users;")
print(cursor.fetchall())
conn.close()
