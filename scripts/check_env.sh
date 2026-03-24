#!/usr/bin/env bash
set -euo pipefail

echo "Checking demo environment..."

if [[ -z "${ELASTICSEARCH_REPO_PATH:-}" ]]; then
  echo "[ERROR] ELASTICSEARCH_REPO_PATH is not set"
  exit 1
fi

if [[ ! -d "$ELASTICSEARCH_REPO_PATH" ]]; then
  echo "[ERROR] ELASTICSEARCH_REPO_PATH is not a directory: $ELASTICSEARCH_REPO_PATH"
  exit 1
fi

if [[ ! -d "$ELASTICSEARCH_REPO_PATH/.git" ]]; then
  echo "[ERROR] ELASTICSEARCH_REPO_PATH does not look like a git repository: $ELASTICSEARCH_REPO_PATH"
  exit 1
fi

if ! command -v mgrep >/dev/null 2>&1; then
  echo "[ERROR] mgrep command not found on PATH"
  exit 1
fi

echo "[OK] Repo path and mgrep command look available"

if [[ -z "${SERENA_COMMAND_TEMPLATE:-}" ]]; then
  echo "[WARN] SERENA_COMMAND_TEMPLATE is not set (Serena mode will fail until configured)"
else
  echo "[OK] SERENA_COMMAND_TEMPLATE is set"
fi
