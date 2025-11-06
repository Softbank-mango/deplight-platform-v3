#!/usr/bin/env bash
set -euo pipefail

SRC_DIR=${1:-lambda/ai_code_analyzer}
OUT_ZIP=${2:-build/ai_analyzer.zip}

mkdir -p "$(dirname "$OUT_ZIP")"

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

rsync -a "$SRC_DIR/" "$tmpdir/"

pushd "$tmpdir" >/dev/null
zip -r "$OLDPWD/$OUT_ZIP" .
popd >/dev/null

echo "Created $OUT_ZIP"

