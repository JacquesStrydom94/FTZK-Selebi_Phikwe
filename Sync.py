import os
import requests
import sqlite3
import base64
import re


#Database ID
DBID=""
# Super Token
Token = ""
################################################-DEVICE TABLE-#####################################################################
# Endpoint URL
Device_url = f'https://appnostic.dbflex.net/secure/api/v2/{DBID}/{Token}/ZK%20Device/select.json'
# Fetch JSON data from the endpoint
Device_response = requests.get(Device_url)
data = Device_response.json()

# Debugging: Print the fetched data
print("Fetched data:", data)

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('PUSH.db')
cursor = conn.cursor()

# Create table if it doesn't exist
table_name = 'DEVICES'
cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, remote_id INTEGER)')

# Function to check if a column exists
def Column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    return column_name in columns

# Check if the column 'remote_id' exists and add it if it doesn't
if not Column_exists(cursor, table_name, 'remote_id'):
    cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN remote_id INTEGER')
    conn.commit()

# Function to sanitize column names
def Sanitize_column_name(name):
    return re.sub(r'\W|^(?=\d)', '_', name)

# Add new columns if they don't exist
for key in data[0].keys():
    if key == 'Id':  # Skip the 'Id' key
        continue
    sanitized_key = Sanitize_column_name(key)
    if not Column_exists(cursor, table_name, sanitized_key):
        cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {sanitized_key} TEXT')

# Insert data into the table
for item in data:
    sanitized_item = {Sanitize_column_name(k): v for k, v in item.items() if k != 'Id'}
    sanitized_item['remote_id'] = item['Id']  # Add 'remote_id' with the value of 'Id'
    columns = ', '.join(sanitized_item.keys())
    placeholders = ', '.join(['?' for _ in sanitized_item])
    insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
    cursor.execute(insert_query, list(sanitized_item.values()))

# Commit changes and close the connection
conn.commit()
conn.close()

print("DEVICES UPDATED.")
################################################-Command TABLE-#####################################################################
# Endpoint URL
Command_url = f'https://appnostic.dbflex.net/secure/api/v2/{DBID}/{Token}/Command/select.json'

# Fetch JSON data from the endpoint
CMD_response = requests.get(Command_url)
data = CMD_response.json()

# Debugging: Print the fetched data
print("Fetched data:", data)

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('PUSH.db')
cursor = conn.cursor()

# Create table if it doesn't exist
table_name = 'COMMAND'
cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, remote_id INTEGER)')

# Function to check if a column exists
def Column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    return column_name in columns

# Check if the column 'remote_id' exists and add it if it doesn't
if not Column_exists(cursor, table_name, 'remote_id'):
    cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN remote_id INTEGER')
    conn.commit()

# Function to sanitize column names
def Sanitize_column_name(name):
    return re.sub(r'\W|^(?=\d)', '_', name)

# Add new columns if they don't exist
for key in data[0].keys():
    if key == 'Id':  # Skip the 'Id' key
        continue
    sanitized_key = Sanitize_column_name(key)
    if not Column_exists(cursor, table_name, sanitized_key):
        cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {sanitized_key} TEXT')

# Insert data into the table
for item in data:
    sanitized_item = {Sanitize_column_name(k): v for k, v in item.items() if k != 'Id'}
    sanitized_item['remote_id'] = item['Id']  # Add 'remote_id' with the value of 'Id'
    columns = ', '.join(sanitized_item.keys())
    placeholders = ', '.join(['?' for _ in sanitized_item])
    insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
    cursor.execute(insert_query, list(sanitized_item.values()))

# Commit changes and close the connection
conn.commit()
conn.close()

print("COMMANDS UPDATED")

################################################-STAFF TABLE-#####################################################################
# Endpoint URL
staff_url = f'https://appnostic.dbflex.net/secure/api/v2/{DBID}/{Token}/Staff/ZK_DATA/select.json'

# Fetch JSON data from the endpoint
staff_response = requests.get(staff_url)
data = staff_response.json()

# Debugging: Print the fetched data
print("Fetched data:", data)

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('PUSH.db')
cursor = conn.cursor()

# Create table if it doesn't exist
table_name = 'STAFF'
cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, remote_id INTEGER)')

# Function to check if a column exists
def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    return column_name in columns

# Check if the column 'remote_id' exists and add it if it doesn't
if not column_exists(cursor, table_name, 'remote_id'):
    cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN remote_id INTEGER')
    conn.commit()

# Function to sanitize column names
def sanitize_column_name(name):
    return re.sub(r'\W|^(?=\d)', '_', name)

# Add new columns if they don't exist
for key in data[0].keys():
    if key == 'Id':  # Skip the 'Id' key
        continue
    sanitized_key = sanitize_column_name(key)
    if not column_exists(cursor, table_name, sanitized_key):
        cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {sanitized_key} TEXT')

# Insert data into the table
for item in data:
    sanitized_item = {sanitize_column_name(k): v for k, v in item.items() if k != 'Id'}
    sanitized_item['remote_id'] = item['Id']  # Add 'remote_id' with the value of 'Id'
    columns = ', '.join(sanitized_item.keys())
    placeholders = ', '.join(['?' for _ in sanitized_item])
    insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
    cursor.execute(insert_query, list(sanitized_item.values()))

# Commit changes and close the connection
conn.commit()
conn.close()


print("STAFF UPDATED")

################################################-STAFF PHOTOS-#####################################################################
import sqlite3
import requests
import base64

# Database connection
conn = sqlite3.connect('push.db')
cursor = conn.cursor()

# Function to fetch data from endpoint and write into SQL
def fetch_and_write(endpoint, table_name):
    response = requests.get(endpoint)
    
    # Check if the response is JSON
    if response.headers.get('Content-Type') == 'application/json':
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Error: Unable to decode JSON from {endpoint}")
            return
        
        # Assuming data is a list of dictionaries
        for record in data:
            columns = ', '.join(record.keys())
            placeholders = ', '.join('?' * len(record))
            sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
            cursor.execute(sql, tuple(record.values()))
        conn.commit()
    else:
        print(f"Error: Response from {endpoint} is not JSON")

# Function to update staff photo
def update_staff_photo(dbid, token, remote_id):
    photo_url = f'https://appnostic.dbflex.net/secure/api/v2/{dbid}/{token}/Staff/Staff Photo/attachment?id={remote_id}'
    response = requests.get(photo_url)
    image_data = response.content
    
    # Convert the image to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Ensure the 'Staff Photo' column exists
    try:
        cursor.execute('ALTER TABLE staff ADD COLUMN "Staff Photo" TEXT')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print("Column 'Staff Photo' already exists.")
        else:
            raise
    
    # Update the existing record in the Staff table
    sql = 'UPDATE staff SET "Staff Photo" = ? WHERE remote_id = ?'
    cursor.execute(sql, (image_base64, remote_id))
    conn.commit()

# Example usage
endpoints = {
    'staff': 'https://example.com/api/staff',
    'departments': 'https://example.com/api/departments'
}

for table, endpoint in endpoints.items():
    fetch_and_write(endpoint, table)

# Update staff photo for multiple remote IDs
remote_ids = [1, 2, 3]  # Example remote IDs

for remote_id in remote_ids:
    update_staff_photo(DBID,Token, remote_id)

# Close the database connection
conn.close()

print("STAFF PHOTOS UPDATED")
