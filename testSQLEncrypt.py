from sqlitesec import SqliteSec
import os

# Initialize with your encryption key
key = os.urandom(32)  # Generate a secure 256-bit key
sqs = SqliteSec(key)

# Create and use encrypted database
conn = sqs.connect("secure.db")
cursor = conn.cursor()

# Standard SQLite operations work normally
cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)')
cursor.execute('INSERT INTO users (name) VALUES (?)', ('Alice',))
conn.commit()

# Always close properly to ensure encryption
sqs.close(conn, "secure.db")

# Reconnect and read data
conn = sqs.connect("secure.db")
cursor = conn.cursor()

cursor.execute('SELECT name FROM users WHERE id = 1')
user_name = cursor.fetchone()[0]
print(f"User: {user_name}")

sqs.close(conn, "secure.db")