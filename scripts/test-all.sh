#!/usr/bin/env bash
# Run all test suites locally (mirrors CI).
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
run "pytest (agent-orchestrator)" bash -c "cd $REPO_ROOT/services/agent-orchestrator && python -m pytest tests/ -v"
run "pytest (control-plane)" bash -c "cd $REPO_ROOT/services/control-plane && python -m pytest tests/ -v"

# Go
run "go test (dpi-engine)" bash -c "cd $REPO_ROOT/sensors/dpi-engine && go test -race ./..."

# Rust
run "cargo test (safety-gate)" bash -c "cd $REPO_ROOT/services/safety-gate && cargo test"

# TypeScript
run "vitest (dashboard)" bash -c "cd $REPO_ROOT/ui/dashboard && npx vitest run"

echo ""
if [[ $ERRORS -eq 0 ]]; then
    echo "All tests passed ✓"
else
    echo "$ERRORS test suite(s) failed ✗"
    exit 1
fi
