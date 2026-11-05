import sqlite3

# Connect to your main database file
conn = sqlite3.connect("puzzgrid_database.db")
cursor = conn.cursor()

# 1. Get total number of saved puzzles
cursor.execute("SELECT COUNT(*) FROM puzzles")
total = cursor.fetchone()[0]
print(f"Total Puzzles Saved: {total}\n")

# 2. Query and display a sample of saved rows
cursor.execute("SELECT * FROM puzzles LIMIT 5")
rows = cursor.fetchall()

# Print column names
column_names = [description[0] for description in cursor.description]
print(f"Columns: {column_names}\n")

for row in rows:
    print(f"--- Grid #{row[0]}: {row[1]} (by {row[2]}) ---")
    print(f"  Group 1: {row[3]}")
    print(f"    Items: {row[4]}")
    print(f"  Group 2: {row[5]}")
    print(f"    Items: {row[6]}")
    print(f"  Group 3: {row[7]}")
    print(f"    Items: {row[8]}")
    print(f"  Group 4: {row[9]}")
    print(f"    Items: {row[10]}")
    print("-" * 50)

conn.close()