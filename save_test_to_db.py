import json
import re
import sqlite3

# 1. Connect to new target database
conn_out = sqlite3.connect("puzzgrid_database.db")
cursor_out = conn_out.cursor()

cursor_out.execute(
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
conn_out.commit()


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


# 2. Read from old puzzgrid_db.db
conn_in = sqlite3.connect("puzzgrid_db.db")
cursor_in = conn_in.cursor()
cursor_in.execute("SELECT id, html_content FROM puzzles")

for grid_id, html in cursor_in.fetchall():
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
    )
    if not match:
        continue

    payload = json.loads(match.group(1))
    page_props = payload.get("props", {}).get("pageProps", {})

    grid_meta = page_props.get("grid", {})
    title = grid_meta.get("title", f"Grid #{grid_id}")
    author = grid_meta.get("author", "Unknown")

    encoded_groups = page_props.get("groups_o", "")
    groups = decode_puzzgrid(encoded_groups)

    g1_n = groups[0].get("description", "") if len(groups) > 0 else ""
    g1_i = ", ".join(groups[0].get("tiles", [])) if len(groups) > 0 else ""
    g2_n = groups[1].get("description", "") if len(groups) > 1 else ""
    g2_i = ", ".join(groups[1].get("tiles", [])) if len(groups) > 1 else ""
    g3_n = groups[2].get("description", "") if len(groups) > 2 else ""
    g3_i = ", ".join(groups[2].get("tiles", [])) if len(groups) > 2 else ""
    g4_n = groups[3].get("description", "") if len(groups) > 3 else ""
    g4_i = ", ".join(groups[3].get("tiles", [])) if len(groups) > 3 else ""

    cursor_out.execute(
        """
        INSERT OR REPLACE INTO puzzles 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (grid_id, title, author, g1_n, g1_i, g2_n, g2_i, g3_n, g3_i, g4_n, g4_i),
    )

conn_out.commit()
conn_in.close()
conn_out.close()
print("Saved test puzzles into puzzgrid_database.db!")