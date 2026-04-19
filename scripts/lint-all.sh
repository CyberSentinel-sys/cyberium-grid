#!/usr/bin/env bash
# Run all linters locally (mirrors CI).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ERRORS=0

run() {
    local name="$1"; shift
    echo ""
    echo "══ $name ══"
    if "$@"; then
        echo "  ✓ $name passed"
    else
        echo "  ✗ $name FAILED"
        ERRORS=$((ERRORS + 1))
    fi
}

# Python
run "ruff (services)" ruff check "$REPO_ROOT/services/agent-orchestrator/src" "$REPO_ROOT/services/control-plane/src"
run "mypy (agent-orchestrator)" mypy --strict "$REPO_ROOT/services/agent-orchestrator/src"

# Go
run "golangci-lint (dpi-engine)" bash -c "cd $REPO_ROOT/sensors/dpi-engine && golangci-lint run ./..."

# Rust
run "clippy (safety-gate)" bash -c "cd $REPO_ROOT/services/safety-gate && cargo clippy -- -D warnings"

# TypeScript
run "eslint (dashboard)" bash -c "cd $REPO_ROOT/ui/dashboard && npx eslint src/"
run "tsc (dashboard)" bash -c "cd $REPO_ROOT/ui/dashboard && npx tsc --noEmit"

echo ""
if [[ $ERRORS -eq 0 ]]; then
    echo "All linters passed ✓"
else
    echo "$ERRORS linter(s) failed ✗"
    exit 1
fi
