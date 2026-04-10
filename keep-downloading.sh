#!/usr/bin/env bash
#
# Usage: nohup ./keep-downloading.sh &
#
# A script that keeps calling 'main.py' sith 4 downloads,
# waiting until the next quarter-hour between each attempt.
# Messages are written (appended) to 'keep-downloading.log'
# and the downloads written to './tmp' (which is wiped before each run).
#
# By synchronising the start of the download to the next quarter-hour
# we do our best to align downloads across multiple machines.
#
# This was designed for #1978 to investigate download speeds
# over long periods of time in order to try and identify a pattern
# (if any) where downloads would 'slow down'.

cmd="uv run main.py 8 lb32627-66 A71EV2A production --verbose"
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

# Sleep until the next quarter-hour boundary (00, 15, 30, or 45 minutes past).
sleep_until_next_quarter_hour() {
  local now_min now_sec secs_past_quarter secs_to_wait
  now_min=$(date +%-M)
  now_sec=$(date +%-S)
  secs_past_quarter=$(( (now_min % 15) * 60 + now_sec ))
  secs_to_wait=$(( 15 * 60 - secs_past_quarter ))
  local next_quarter
  next_quarter=$(date -v +${secs_to_wait}S '+%H:%M')
  echo $(date '+%Y-%m-%d %H:%M') Waiting ${secs_to_wait}s until next quarter-hour \(${next_quarter}\) ... >> ${log}
  sleep ${secs_to_wait}
}

download=1
sleep_until_next_quarter_hour
while true
do
  echo $(date '+%Y-%m-%d %H:%M') Wiping: ${download_directory}
  rm -rf ${download_directory}
  echo $(date '+%Y-%m-%d %H:%M') Downloading: ${download} >> ${log}
  $cmd >> ${log} 2>&1
  sleep_until_next_quarter_hour
  echo --- >> ${log}
  ((download++))
done
