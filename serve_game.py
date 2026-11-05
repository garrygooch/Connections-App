"""Serve only the two public game assets on localhost."""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = {'/': ('index.html', 'text/html; charset=utf-8'), '/index.html': ('index.html', 'text/html; charset=utf-8'), '/puzzles.json': ('puzzles.json', 'application/json; charset=utf-8')}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        asset = ASSETS.get(self.path.split('?', 1)[0])
        if asset is None:
            self.send_error(404)
            return
        data = (ROOT / asset[0]).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', asset[1])
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

if __name__ == '__main__':
    print('Open http://127.0.0.1:8001', flush=True)
    HTTPServer(('127.0.0.1', 8001), Handler).serve_forever()
