import os
import sqlite3
import csv

file_path = "facilityDB.db"
if os.path.exists(file_path):
    os.remove(file_path)

# Establish a connection to the SQLite database (creates the database if
# it doesn't exist)
conn = sqlite3.connect("facilityDB.db")

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table (if it doesn't already exist)
cursor.execute("""
CREATE TABLE IF NOT EXISTS facilityDBCategories (
    id INTEGER PRIMARY KEY,
    category TEXT
)
""")

# Open the CSV file
with open("csvInventoryCategories.csv", "r") as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)

    # Skip the header row
    next(csv_reader)

    # Insert each row into the table
    for row in csv_reader:
        cursor.execute(
            """
        INSERT INTO facilityDBCategories (id, category) VALUES (?, ?)
        """,
            row,
        )

# Commit changes and close the connection
conn.commit()
conn.close()

# Establish a connection to the SQLite database (creates the database if
# it doesn't exist)
conn = sqlite3.connect("facilityDB.db")

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table (if it doesn't already exist)
cursor.execute("""
CREATE TABLE IF NOT EXISTS facilityDBInventory (
    id INTEGER PRIMARY KEY,
    category TEXT,
    item TEXT,
    goal INTEGER,
    have INTEGER
)
""")

# Open the CSV file
with open("csvInventoryForExport.csv", "r") as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)

    # Skip the header row
    next(csv_reader)

    # Insert each row into the table
    for row in csv_reader:
        cursor.execute(
            """
INSERT INTO facilityDBInventory (
    id, category, item, goal, have
) VALUES (?, ?, ?, ?, ?)
""",
            row,
        )

# Commit changes and close the connection
conn.commit()
conn.close()

conn = sqlite3.connect("facilityDB.db")

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table (if it doesn't already exist)
cursor.execute("""
CREATE TABLE IF NOT EXISTS facilityDBUsers (
    id INTEGER PRIMARY KEY,
    firstName TEXT,
    lastName TEXT,
    eMail TEXT,
    userName TEXT,
    permissions TEXT,
    passWord TEXT,
    resetStatus BOOL,
    resetCode TEXT
)
""")

# Open the CSV file
with open("csvUsersForExport.csv", "r") as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)

    # Skip the header row
    next(csv_reader)

    # Insert each row into the table
    for row in csv_reader:
        # print(row)
        cursor.execute(
            """
INSERT INTO facilityDBUsers (
    id, firstName, lastName, eMail, userName, permissions, passWord, resetStatus, resetCode
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""",
            row,
        )

# Commit changes and close the connection
conn.commit()
conn.close()
