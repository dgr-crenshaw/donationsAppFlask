import sqlite3

with sqlite3.connect('/home/dgrCrenshaw/donationsAppFlask/facilityDB.db') as conn:

    cursor = conn.cursor()

    # Query sqlite_master for tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # Fetch all results (returns a list of tuples)/home/dgrCrenshaw/donationsAppFlask/
    table_names = cursor.fetchall()

    # Extract table names from tuples (each result is (name,))
    table_names = [name[0] for name in table_names]

print("Table names:", table_names)

conn.close()