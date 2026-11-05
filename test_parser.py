import json
import re
import sqlite3

conn = sqlite3.connect("puzzgrid_db.db")
cursor = conn.cursor()

cursor.execute("SELECT id, html_content FROM puzzles")
rows = cursor.fetchall()

for puzzle_id, html in rows:
    # Look for Next.js __NEXT_DATA__ payload or embedded state script
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
    )

    if match:
        data = json.loads(match.group(1))
        print(f"--- Grid #{puzzle_id} (Extracted JSON) ---")
        # Print main page props / grid payload
        print(json.dumps(data, indent=2)[:400])
        print("...\n")
    else:
        # Fallback regex search for embedded grid JavaScript object
        grid_match = re.search(r"gridData\s*=\s*(\{.*?\});", html)
        if grid_match:
            print(f"--- Grid #{puzzle_id} (Grid Data) ---")
            print(grid_match.group(1)[:400])
            print("...\n")
        else:
            print(f"Grid #{puzzle_id}: No direct JSON object regex match found.")

conn.close()