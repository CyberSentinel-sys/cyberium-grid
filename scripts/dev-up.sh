#!/usr/bin/env bash
# Bring up the full OrHaShield dev stack.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/infra/docker-compose.yml"

# Bootstrap .env if it doesn't exist
if [[ ! -f "$REPO_ROOT/.env" ]]; then
    cp "$REPO_ROOT/.env.example" "$REPO_ROOT/.env"
    echo "[!] Created .env from .env.example — please set ANTHROPIC_API_KEY before continuing."
    echo "    Edit: $REPO_ROOT/.env"
    exit 1
fi

# Validate mandatory variables
REQUIRED=(ANTHROPIC_API_KEY POSTGRES_PASSWORD NATS_SENSOR_PASS NATS_AGENT_PASS NATS_GATEWAY_PASS NATS_CP_PASS)
missing=()
# shellcheck disable=SC2046
eval $(grep -v '^#' "$REPO_ROOT/.env" | sed 's/^/export /' | grep -E '^export [A-Z_]+=')
for var in "${REQUIRED[@]}"; do
    [[ -z "${!var:-}" ]] && missing+=("$var")
done

if [[ ${#missing[@]} -gt 0 ]]; then
    echo "[!] Missing required env vars: ${missing[*]}"
    echo "    Fill them in $REPO_ROOT/.env"
    exit 1
fi

echo "[*] Starting OrHaShield dev stack…"
docker compose -f "$COMPOSE_FILE" --env-file "$REPO_ROOT/.env" up -d "$@"

echo ""
echo "  Services:"
echo "    Control Plane  → http://localhost:8000"
echo "    Dashboard      → http://localhost:3000"
echo "    NATS Monitor   → http://localhost:8222"
echo "    Prometheus     → http://localhost:9090"
echo "    Grafana        → http://localhost:3001  (admin / \$GRAFANA_PASSWORD)"
echo "    Neo4j Browser  → http://localhost:7474"
echo "    Qdrant         → http://localhost:6333"
echo ""
echo "[*] Done. Use 'docker compose -f infra/docker-compose.yml logs -f' to stream logs."
