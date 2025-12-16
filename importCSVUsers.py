# Import required modules
import sqlite3  # For SQLite database operations
import csv      # For handling CSV files

conn = sqlite3.connect('facilityDB.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table (if it doesn't already exist)
cursor.execute('''
CREATE TABLE IF NOT EXISTS facilityDBUsers (
    id INTEGER PRIMARY KEY,
    firstName TEXT,
    lastName TEXT,
    eMail TEXT,
    userName TEXT,
    passWord TEXT,
    resetStatus BOOL,
    resetCode TEXT
)
''')

# Open the CSV file
with open('csvUsersForExport.csv', 'r') as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)

    # Skip the header row
    next(csv_reader)

    # Insert each row into the table
    for row in csv_reader:
        print(row)
        cursor.execute('''
        INSERT INTO facilityDBUsers (id, firstName, lastName, eMail, userName, passWord, resetStatus, resetCode) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', row)

# Commit changes and close the connection
conn.commit()
conn.close()