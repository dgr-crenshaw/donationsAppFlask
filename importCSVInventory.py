# Import required modules
import sqlite3  # For SQLite database operations
import csv      # For handling CSV files

# Establish a connection to the SQLite database (creates the database if it doesn't exist)
conn = sqlite3.connect('faciityDB.db')
#   conn = sqlite3.connect('faciityDB.db'

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table (if it doesn't already exist)
cursor.execute('''
CREATE TABLE IF NOT EXISTS faciityDBInventory (
    id INTEGER PRIMARY KEY,
    category TEXT,
    item TEXT,
    goal INTEGER,
    have INTEGER
)
''')

# Open the CSV file
with open('csvInventoryForExport.csv', 'r') as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)

    # Skip the header row
    next(csv_reader)

    # Insert each row into the table
    for row in csv_reader:
        cursor.execute('''
        INSERT INTO faciityDBInventory (id, category, item, goal, have) VALUES (?, ?, ?, ?, ?)
        ''', row)

# Commit changes and close the connection
conn.commit()
conn.close()