"""Run server and browser in one process tree."""
import os
import subprocess
import threading
from pathlib import Path
from proof.walk.__main__ import make_server

server = make_server(0)
threading.Thread(target=server.serve_forever, daemon=True).start()
env = dict(os.environ, SCENE_URL=f'http://127.0.0.1:{server.server_port}')
try:
    result = subprocess.run(['node', str(Path(__file__).with_name('browser.cjs'))], env=env)
finally:
    server.shutdown()
    server.server_close()
raise SystemExit(result.returncode)
