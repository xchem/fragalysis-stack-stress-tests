#!/usr/bin/env bash
#
# Usage: nohup ./keep-downloading.sh [concurrency] [environment] &
#
# A script that keeps calling 'main.py' with 8 (default) downloads,
# waiting until the next 20-minute boundary between each attempt.
# Messages are written (appended) to 'keep-downloading.log'
# and the downloads written to './tmp' (which is wiped before each run).
#
# By waiting until the start of the download to the next period
# we do our best to synchronise downloads across multiple machines.
#
# This was designed for #1978 to investigate download speeds
# over long periods of time in order to try and identify a pattern
# (if any) where downloads would 'slow down'.
#
# You can add --verbose to the command to see task status change messages
# You can add --debug to see request/response debug (a lot of output is generated)

concurrency="${1:-8}"
environment="${2:-production}"
cmd="uv run main.py ${concurrency} lb32627-66 A71EV2A ${environment}"
log="keep-downloading.log"
# The default download directory.
# Be VERY careful - we wipe it so it MUST be local.
# This is not completely safe but it must start with '.'.
download_directory="./tmp"

if  [[ ! $download_directory == .* ]] ;
then
    echo "ERROR: Download directory must start with '.' (it cannot be $download_directory)"
    exit 1
fi

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

download=1
sleep_until_next_20_minutes
while true
do
  echo $(date '+%Y-%m-%d %H:%M') Wiping ${download_directory} >> ${log}
  rm -rf ${download_directory}
  echo $(date '+%Y-%m-%d %H:%M') Starting download iteration ${download} >> ${log}
  $cmd >> ${log} 2>&1
  sleep_until_next_20_minutes
  echo --- >> ${log}
  ((download++))
done
