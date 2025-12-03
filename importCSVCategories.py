# Import required modules
import sqlite3  # For SQLite database operations
import csv      # For handling CSV files

# Establish a connection to the SQLite database (creates the database if it doesn't exist)
conn = sqlite3.connect('/home/dgrCrenshaw/donationsAppFlask/facilityDB.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table (if it doesn't already exist)
cursor.execute('''
CREATE TABLE IF NOT EXISTS facilityDBCategories (
    id INTEGER PRIMARY KEY,
    category TEXT
)
''')

# Open the CSV file
with open('csvInventoryCategories.csv', 'r') as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)

    # Skip the header row
    next(csv_reader)

    # Insert each row into the table
    for row in csv_reader:
        cursor.execute('''
        INSERT INTO facilityDBCategories (id, category) VALUES (?, ?)
        ''', row)

# Commit changes and close the connection
conn.commit()
conn.close()