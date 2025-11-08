#!/usr/bin/env bash
set -euo pipefail

STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"

python -c "import streamlit" >/dev/null 2>&1 || {
  echo "[error] streamlit 미설치. 설치: pip install streamlit" >&2
  exit 1
}

exec streamlit run app/streamlit_app.py --server.port "$STREAMLIT_PORT" --server.headless true

