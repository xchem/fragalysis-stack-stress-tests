#!/usr/bin/env bash
#
# Usage: nohup ./keep-sequencing.sh [concurrency] [host] &
#
# A script that keeps calling 'main.py sequence' with 8 (default) concurrent
# replays of the API call sequence, waiting until the next 20-minute boundary
# between each attempt. Messages are written (appended) to 'keep-sequencing.log'.
#
# By waiting until the start of the run to the next period
# we do our best to synchronise sequences across multiple machines.

concurrency="${1:-8}"
host="${2:-fragalysis.diamond.ac.uk}"
cmd="uv run main.py sequence ${concurrency} ${host}"
log="keep-sequencing.log"

# Sleep until the next 20-minute boundary (00, 20, or 40 minutes past).
sleep_until_next_20_minutes() {
  local now_min now_sec secs_past_period secs_to_wait
  now_min=$(date +%-M)
  now_sec=$(date +%-S)
  secs_past_period=$(( (now_min % 20) * 60 + now_sec ))
  secs_to_wait=$(( 20 * 60 - secs_past_period ))
  local next_period
  next_period=$(date -d "+${secs_to_wait} seconds" '+%H:%M' 2>/dev/null || date -v +${secs_to_wait}S '+%H:%M')
  echo $(date '+%Y-%m-%d %H:%M') Waiting until \(${next_period}\) ... >> ${log}
  sleep ${secs_to_wait}
}

rm -f ${log}
iteration=1
sleep_until_next_20_minutes
while true
do
  echo $(date '+%Y-%m-%d %H:%M') Starting sequence iteration ${iteration} >> ${log}
  $cmd >> ${log} 2>&1
  sleep_until_next_20_minutes
  echo --- >> ${log}
  ((iteration++))
done
