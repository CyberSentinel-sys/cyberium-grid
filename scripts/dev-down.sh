#!/usr/bin/env bash
# Tear down the OrHaShield dev stack (preserves volumes by default).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/infra/docker-compose.yml"

echo "[*] Stopping OrHaShield dev stack…"
docker compose -f "$COMPOSE_FILE" down "$@"
echo "[*] Done. Volumes are preserved. Use --volumes to also delete data."
