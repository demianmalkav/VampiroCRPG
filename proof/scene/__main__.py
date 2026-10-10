"""Loopback-only stdlib server. No hosting, authentication or production claims."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import webbrowser

from proof.m2.world import InvalidSnapshot, Rejected
from .session import Session

ROOT = Path(__file__).resolve().parent
MAX_BODY = 2 * 1024 * 1024


def make_server(port=8765):
    session = Session()
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, status, body, mime='application/json; charset=utf-8', download=False):
            if not isinstance(body, bytes):
                body = json.dumps(body, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' blob:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
            if download:
                self.send_header('Content-Disposition', 'attachment; filename="noche-guardada.json"')
            self.end_headers()
            self.wfile.write(body)

        def allowed(self):
            hosts = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
            origin = self.headers.get('Origin')
            return self.headers.get('Host') in hosts and (not origin or origin in {'http://' + h for h in hosts})

        def do_GET(self):
            if not self.allowed():
                return self.send(403, {'error': 'ORIGIN_REJECTED'})
            with lock:
                if self.path == '/api/view':
                    return self.send(200, session.view())
                if self.path == '/api/save':
                    return self.send(200, session.save().encode('utf-8'), download=True)
            assets = {'/': ('index.html', 'text/html; charset=utf-8'), '/scene.css': ('scene.css', 'text/css; charset=utf-8'), '/scene.js': ('scene.js', 'text/javascript; charset=utf-8')}
            if self.path in assets:
                file, mime = assets[self.path]
                return self.send(200, (ROOT/file).read_bytes(), mime)
            self.send(404, {'error': 'NOT_FOUND'})

        def do_POST(self):
            if not self.allowed():
                return self.send(403, {'error': 'ORIGIN_REJECTED'})
            if self.path != '/api/action':
                return self.send(404, {'error': 'NOT_FOUND'})
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= MAX_BODY or self.headers.get_content_type() != 'application/json':
                    return self.send(400, {'error': 'INVALID_BODY'})
                def unique(pairs):
                    result = {}
                    for k, v in pairs:
                        if k in result: raise ValueError('DUPLICATE_JSON_KEY')
                        result[k] = v
                    return result
                request = json.loads(self.rfile.read(size), object_pairs_hook=unique, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('INVALID_CONSTANT')))
                with lock:
                    self.send(200, session.mutate(request))
            except (Rejected, InvalidSnapshot, ValueError, TypeError, KeyError) as exc:
                self.send(409, {'error': str(exc)})

    server = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    server.scene_session = session
    return server


def main():
    parser = argparse.ArgumentParser(description='La Noche que Recuerda — escena isométrica mínima')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--open', action='store_true', help='Abrir la escena en tu navegador')
    args = parser.parse_args()
    server = make_server(args.port)
    url = f'http://127.0.0.1:{server.server_port}'
    print(f'Escena lista: {url}\nCtrl+C para cerrar.', flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
