# Connections App

Serve this folder over HTTP (opening index.html directly will not load puzzle data):

```powershell
python serve_game.py
```

Then open http://127.0.0.1:8001 and click Start Game. Select four related tiles; matching groups are checked automatically. The wall has a three-minute timer, with three lives once two groups are solved. Next Puzzle starts a different wall.

Rebuild the frontend data with `python export_puzzles.py`. The exporter reads puzzgrid_database.db without modifying it, validates four groups of four unique nonempty tiles, and writes puzzles.json plus export_report.json. The empty puzzgrid_clean.db is not used. Existing comma-space storage cannot reliably recover embedded separators; ambiguous or incomplete records are skipped.

Run gameplay smoke checks with `node verify_game.cjs`.

## Public game

GitHub Actions publishes the game to https://garrygooch.github.io/Connections-App/ after changes are pushed to main. Only index.html, puzzles.json, sounds/, and images/ are included in the deployment.

Played puzzle history is saved in each browser profile. Clearing browser storage or switching devices resets that history. All connections remain hidden until individually revealed at the end of a wall.
