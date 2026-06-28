#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export STORM_FLEET_ROOT="${STORM_FLEET_ROOT:-$ROOT}"
export STORM_SESSION="${STORM_SESSION:-STORM BOSS}"
export STORM_LAYOUT="${STORM_LAYOUT:-$STORM_FLEET_ROOT/layouts/fleet.kdl}"
export STORM_POLICY="${STORM_POLICY:-$STORM_FLEET_ROOT/state/fleet-policy.env}"
export STORM_WORKERS="${STORM_WORKERS:-$STORM_FLEET_ROOT/workers.tsv}"
export STORM_DISPATCH_LEDGER="${STORM_DISPATCH_LEDGER:-$STORM_FLEET_ROOT/state/dispatch-ledger.tsv}"
export STORM_SKILL_REGISTRY="${STORM_SKILL_REGISTRY:-$STORM_FLEET_ROOT/state/skill-registry.tsv}"
export STORM_RUNTIME_DIR="${STORM_RUNTIME_DIR:-$STORM_FLEET_ROOT/.storm-runtime}"

if [[ -r "$STORM_POLICY" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$STORM_POLICY"
  set +a
fi

mkdir -p "$STORM_RUNTIME_DIR"
