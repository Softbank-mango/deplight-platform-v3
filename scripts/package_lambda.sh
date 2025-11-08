#!/usr/bin/env bash
set -euo pipefail

SRC_DIR=${1:-lambda/ai_code_analyzer}
OUT_ZIP=${2:-build/ai_analyzer.zip}

mkdir -p "$(dirname "$OUT_ZIP")"

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

rsync -a "$SRC_DIR/" "$tmpdir/"

# Move package/* to root for Lambda to find dependencies
if [ -d "$tmpdir/package" ]; then
    echo "Moving package contents to root..."
    rsync -a "$tmpdir/package/" "$tmpdir/"
    rm -rf "$tmpdir/package"
fi

pushd "$tmpdir" >/dev/null
zip -r "$OLDPWD/$OUT_ZIP" .
popd >/dev/null

echo "Created $OUT_ZIP"

