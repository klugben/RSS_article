#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/root/tencent_rsync_mac/RSS_article"
PYTHON_BIN="${PYTHON_BIN:-python3}"

cd "$BASE_DIR"
"$PYTHON_BIN" "$BASE_DIR/export_lumen_to_output.py"
