import json
import re
import sqlite3
import time
import requests

# 1. Connect / Initialize SQLite Database
conn = sqlite3.connect("puzzgrid_database.db")
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS puzzles (
        id INTEGER PRIMARY KEY,
        title TEXT,
        author TEXT,
        group_1_name TEXT,
        group_1_items TEXT,
        group_2_name TEXT,
        group_2_items TEXT,
        group_3_name TEXT,
        group_3_items TEXT,
        group_4_name TEXT,
        group_4_items TEXT
    )
"""
)
conn.commit()


# 2. Cipher Decoder Function
def decode_puzzgrid(encoded_str):
    decoded = "".join(chr(ord(c) - 3) for c in encoded_str)
    formatted_json = (
        decoded.replace("^", "[")
        .replace("`", "]")
        .replace("~", "{")
        .replace("\x7f", "}")
        .replace("%", '"')
        .replace("#", " ")
        .replace("_q", "\n")
    )
    return json.loads(formatted_json)


# 3. Check already downloaded IDs (Resumable feature)
cursor.execute("SELECT id FROM puzzles")
already_downloaded = set(row[0] for row in cursor.fetchall())
print(f"Already saved in database: {len(already_downloaded)} puzzles")

# Set maximum known grid ID and range
max_id = 124250
total_target = 15419
min_id = max_id - total_target

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

saved_count = 0

print(f"Starting download loop from Grid #{max_id} down to #{min_id}...\n")

for grid_id in range(max_id, min_id, -1):
    if grid_id in already_downloaded:
        continue

    url = f"https://puzzgrid.com/grid/{grid_id}"

    try:
        res = requests.get(url, headers=headers)

        if res.status_code == 200:
            match = re.search(
                r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                res.text,
            )
            if match:
                payload = json.loads(match.group(1))
                page_props = payload.get("props", {}).get("pageProps", {})

                # Extract metadata
                grid_meta = page_props.get("grid", {})
                title = grid_meta.get("title", f"Grid #{grid_id}")
                author = grid_meta.get("author", "Unknown")

                # Decode answers
                encoded_groups = page_props.get("groups_o", "")
                if encoded_groups:
                    groups = decode_puzzgrid(encoded_groups)

                    g1_n = (
                        groups[0].get("description", "")
                        if len(groups) > 0
                        else ""
                    )
                    g1_i = (
                        ", ".join(groups[0].get("tiles", []))
                        if len(groups) > 0
                        else ""
                    )

                    g2_n = (
                        groups[1].get("description", "")
                        if len(groups) > 1
                        else ""
                    )
                    g2_i = (
                        ", ".join(groups[1].get("tiles", []))
                        if len(groups) > 1
                        else ""
                    )

                    g3_n = (
                        groups[2].get("description", "")
                        if len(groups) > 2
                        else ""
                    )
                    g3_i = (
                        ", ".join(groups[2].get("tiles", []))
                        if len(groups) > 2
                        else ""
                    )

                    g4_n = (
                        groups[3].get("description", "")
                        if len(groups) > 3
                        else ""
                    )
                    g4_i = (
                        ", ".join(groups[3].get("tiles", []))
                        if len(groups) > 3
                        else ""
                    )

                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO puzzles 
                        (id, title, author, group_1_name, group_1_items, group_2_name, group_2_items, group_3_name, group_3_items, group_4_name, group_4_items)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            grid_id,
                            title,
                            author,
                            g1_n,
                            g1_i,
                            g2_n,
                            g2_i,
                            g3_n,
                            g3_i,
                            g4_n,
                            g4_i,
                        ),
                    )
                    conn.commit()
                    saved_count += 1
                    print(f"[{saved_count}] Saved Grid #{grid_id}: {title}")

        elif res.status_code == 404:
            print(f"Grid #{grid_id} not found (404), skipping.")

    except Exception as e:
        print(f"Error fetching Grid #{grid_id}: {e}")

    # Delay between requests to avoid server throttling
    time.sleep(1.0)

conn.close()
print("\nBatch download complete!")