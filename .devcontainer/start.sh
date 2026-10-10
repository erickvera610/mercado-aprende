#!/usr/bin/env bash
# Solo para Codespaces: inicia Flask y deja el log fuera del historial Git.
set -eu
if ! python -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1:5000", timeout=2)' >/dev/null 2>&1; then
  mkdir -p instance
  nohup python -m flask --app app:create_app run --host=0.0.0.0 --port=5000 > instance/server.log 2>&1 < /dev/null &
fi
