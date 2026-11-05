import json
import re
import sqlite3


def decode_puzzgrid(encoded_str):
    """Decodes PuzzGrid's ASCII shift cipher."""
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


conn = sqlite3.connect("puzzgrid_db.db")
cursor = conn.cursor()

cursor.execute("SELECT id, html_content FROM puzzles")
rows = cursor.fetchall()

for grid_id, html in rows:
    print(f"\n==================== GRID #{grid_id} ====================")

    # 1. Extract Next.js payload
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
    )
    if not match:
        print("Could not find __NEXT_DATA__ payload.")
        continue

    payload = json.loads(match.group(1))
    page_props = payload.get("props", {}).get("pageProps", {})

    # 2. Extract Metadata (Title, Author)
    grid_meta = page_props.get("grid", {})
    title = grid_meta.get("title", f"Grid #{grid_id}")
    author = grid_meta.get("author", "Unknown")

    print(f"Title:  {title}")
    print(f"Author: {author}\n")

    # 3. Decode & Print the 4 Groups + Answers
    encoded_groups = page_props.get("groups_o", "")
    if encoded_groups:
        try:
            groups = decode_puzzgrid(encoded_groups)

            for idx, group in enumerate(groups, 1):
                category_name = group.get("description", "No description")
                words = ", ".join(group.get("tiles", []))
                print(f"  Group {idx}: {category_name}")
                print(f"  Words:   {words}\n")

        except Exception as e:
            print(f"Decoding failed: {e}")
    else:
        print("No encoded groups found in page payload.")

conn.close()