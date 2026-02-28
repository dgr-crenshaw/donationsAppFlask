import sqlite3

conn = sqlite3.connect('/home/dgrCrenshaw/donationsAppFlask/facilityDB.db')
cur = conn.cursor()
cur.execute('SELECT * FROM facilityDBCategories')
rows = cur.fetchall()
conn.close()
for row in rows:
   print(row)