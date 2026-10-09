"""Run the real JS frontend harness and authority in one local process tree."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from proof.scene.__main__ import make_server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--report')
    args = parser.parse_args()
    server = make_server(0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        env = dict(os.environ, SCENE_URL=f'http://127.0.0.1:{server.server_port}')
        result = subprocess.run(['node', str(Path(__file__).with_name('check-ui.cjs'))], env=env, capture_output=True, text=True, timeout=20)
        print(result.stdout, end=''); print(result.stderr, end='', file=sys.stderr)
        if args.report and result.returncode == 0:
            report = json.loads(result.stdout)
            report['authority'] = 'local ephemeral loopback server'
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        return result.returncode
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=2)


if __name__ == '__main__': raise SystemExit(main())
