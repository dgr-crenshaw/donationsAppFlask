import sqlite3

conn = sqlite3.connect('faciityDB.db')
cur = conn.cursor()
cur.execute('SELECT * FROM faciityDBInventory')
rows = cur.fetchall()
conn.close()
for row in rows:
   print(row)