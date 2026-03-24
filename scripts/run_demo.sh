#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <mode> <query> [extra-cli-args...]"
  echo "Example: $0 mgrep \"Where are thread pools defined?\""
  exit 1
fi

MODE="$1"
QUERY="$2"
shift 2

python -m app.cli --mode "$MODE" --query "$QUERY" "$@"
