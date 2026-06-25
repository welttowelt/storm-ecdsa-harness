#!/usr/bin/env bash
# regen-drop-dead-idx.sh — regenerate the drop-dead (dead-gate-elimination) .idx for an EDITED op stream.
#
# Companion to circuit-edit-desync-diagnostic.sh. After a STALE-INDEX verdict, regen the dead-CCX index
# against the EDITED stream so the drops remove the correct (now-shifted) logical ops. Implements the
# "regenerate every stream-specific optimization after any op-stream edit" rule from circuit-edit-integration-safety.md.
#
# Usage:
#   regen-drop-dead-idx.sh <checkout> <nonce> [EDIT_ENV ...] > new_drop.idx
# Notes:
#  - SAMPLING (default) is NOT value-exact: false-dead gates fire on unseed-sampled nonces. For a
#    submission / value-exact result, pass DEAD_SCAN_REAL_SEED=1 (lock the nonce to its .idx) and/or
#    sample many nonces and intersect. Exhaustive proof is the only fully value-exact option.
#  - Requires dead_ccx_scan (src/bin/find_dead_ccx.rs) built in the checkout.

set -euo pipefail
ck="${1:?usage: $0 <checkout> <nonce> [EDIT_ENV...]}"
nonce="${2:?need a nonce}"
shift 2 || true

cd "$ck"
BIN="./target/release"
SCAN="${DEAD_SCAN_BIN:-$BIN/find_dead_ccx}"
[ -x "$SCAN" ] || { echo "build find_dead_ccx first (cargo build --release --bin find_dead_ccx)" >&2; exit 1; }

# Sample N nonces around the target, scan each with the EDIT stream, intersect the dead-op sets.
N="${DEAD_SCAN_SAMPLES:-8}"
echo "# regen-drop-dead-idx: checkout=$ck target_nonce=$nonce edit=[$*] samples=$N real_seed=${DEAD_SCAN_REAL_SEED:-0}" >&2

base=$(( nonce - (N/2) * 1000003 ))   # spread sample nonces around the target
: > /tmp/_regen_intersect.idx
first=1
for i in $(seq 0 $((N-1))); do
  n=$(( base + i * 1000003 ))
  if [ "${DEAD_SCAN_REAL_SEED:-0}" = "1" ]; then n=$nonce; fi   # lock to the target nonce
  # shellcheck disable=SC2086
  out=$(env DIALOG_TAIL_NONCE="$n" "$@" "$SCAN" 2>/dev/null || true)
  if [ $first -eq 1 ]; then
    printf '%s\n' "$out" > /tmp/_regen_intersect.idx
    first=0
  else
    # intersect with the running set (an op is "safely dead" only if dead across ALL sampled nonces)
    comm -12 <(sort /tmp/_regen_intersect.idx) <(printf '%s\n' "$out" | sort) > /tmp/_regen_next.idx
    mv /tmp/_regen_next.idx /tmp/_regen_intersect.idx
  fi
  echo "  sample $i nonce=$n dead_set_size=$(wc -l </tmp/_regen_intersect.idx)" >&2
done
cat /tmp/_regen_intersect.idx
echo "# done. value-exact only if DEAD_SCAN_REAL_SEED=1 (per-nonce) or exhaustive proof; sampling is a lower bound." >&2
