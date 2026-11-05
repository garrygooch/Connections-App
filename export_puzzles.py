import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def export_puzzles(database=ROOT / 'puzzgrid_database.db', output=ROOT / 'puzzles.json'):
    database, output = Path(database).resolve(), Path(output)
    puzzles, rejected = [], []
    with sqlite3.connect(database.as_uri() + '?mode=ro', uri=True) as conn:
        conn.row_factory = sqlite3.Row
        if conn.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Database integrity check failed')
        for row in conn.execute('SELECT * FROM puzzles ORDER BY id'):
            try:
                groups = []
                for i in range(1, 5):
                    raw = row[f'group_{i}_items']
                    # The scraper joined tiles with comma-space without escaping.
                    # Ambiguous rows must be skipped rather than guessing boundaries.
                    items = json.loads(raw) if raw.startswith('[') else raw.split(', ')
                    category = row[f'group_{i}_name']
                    if not isinstance(items, list) or len(items) != 4 or not all(isinstance(x, str) and x.strip() for x in items):
                        raise ValueError(f'Group {i}: expected four nonempty items')
                    if not category or not category.strip():
                        raise ValueError(f'Group {i}: missing category')
                    groups.append({'category': category, 'items': items})
                if len({x.casefold().strip() for g in groups for x in g['items']}) != 16:
                    raise ValueError('Duplicate tiles')
                puzzles.append({'id': str(row['id']), 'title': row['title'], 'author': row['author'], 'groups': groups})
            except (ValueError, TypeError, AttributeError) as exc:
                rejected.append({'id': str(row['id']), 'reason': str(exc)})
    if not puzzles:
        raise ValueError('No valid puzzles; output has not been overwritten')
    output.write_text(json.dumps(puzzles, indent=2, ensure_ascii=False), encoding='utf-8')
    output.with_name('export_report.json').write_text(json.dumps({'exported': len(puzzles), 'skipped': rejected}, indent=2), encoding='utf-8')
    print(f'Exported {len(puzzles)} puzzles; skipped {len(rejected)}. Details: export_report.json')
    return puzzles

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', type=Path, default=ROOT / 'puzzgrid_database.db')
    parser.add_argument('--output', type=Path, default=ROOT / 'puzzles.json')
    args = parser.parse_args()
    export_puzzles(args.database, args.output)
