#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8000}"

python -c "import uvicorn" >/dev/null 2>&1 || {
  echo "[info] FastAPI 의존성 설치"
  pip install -r demo_service/requirements.txt
}

exec uvicorn demo_service.app:app --host 0.0.0.0 --port "$PORT"

