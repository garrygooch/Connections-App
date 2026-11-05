import sqlite3

# Connect to the file that holds your 4 rows
conn = sqlite3.connect("puzzgrid_db.db")
cursor = conn.cursor()

# Get table structure (column names)
cursor.execute("PRAGMA table_info(puzzles);")
columns = [col[1] for col in cursor.fetchall()]
print(f"Table Columns: {columns}\n")

# Retrieve and display all saved rows
cursor.execute("SELECT * FROM puzzles")
rows = cursor.fetchall()

for row in rows:
    puzzle_id = row[0]
    # Grab the first 250 characters of the content to preview
    content_snippet = str(row[1])[:250].replace("\n", " ")
    print(f"--- Grid #{puzzle_id} ---")
    print(f"Preview: {content_snippet}...")
    print()

conn.close()