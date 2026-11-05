import sqlite3
import time
import requests
from bs4 import BeautifulSoup

# Initialize Database
conn = sqlite3.connect("puzzgrid_db.db")
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS puzzles (
        id INTEGER PRIMARY KEY,
        html_content TEXT
    )
"""
)
conn.commit()

puzzle_ids = [124250, 124241, 124237, 124236]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for grid_id in puzzle_ids:
    # Use the actual web page URL format
    url = f"https://puzzgrid.com/grid/{grid_id}"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract full HTML or target specific elements containing the grid words/answers
            cursor.execute(
                "INSERT OR REPLACE INTO puzzles (id, html_content) VALUES (?, ?)",
                (grid_id, response.text),
            )
            conn.commit()
            print(f"Successfully saved grid #{grid_id}")
        else:
            print(f"Failed to fetch #{grid_id}: Status {response.status_code}")

    except Exception as e:
        print(f"Error fetching #{grid_id}: {e}")

    time.sleep(1.5)

conn.close()
print("Finished downloading grid batch.")