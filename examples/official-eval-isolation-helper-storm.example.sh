#!/usr/bin/env bash
for nonce in "$@"; do
  ./ev.sh "$nonce" &
done
wait
