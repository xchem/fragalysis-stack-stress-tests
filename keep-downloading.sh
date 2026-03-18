#!/usr/bin/env bash
#
# Usage: ./keep-downloading.sh
#
# A script that keeps calling 'download_target_stress_test.py',
# pausing for 45 minutes between each attempt.
# The output is written (appended) to 'keep-downloading.log'.
#
# This was designed for #1978 to investigate download speeds
# over long periods of time in order to try and identify a pattern
# (if any) where downloads would 'slow down'.

cmd="uv run main.py"
log="keep-downloading.log"
delay="45m"

download=1
while true
do
  echo $(date '+%Y-%m-%d %H:%M') Download: ${download} >> ${log}
  $cmd >> ${log} 2>&1
  echo $(date '+%Y-%m-%d %H:%M') Sleeping ${delay} ... >> ${log}
  sleep ${delay}
  echo --- >> ${log}
  ((download++))
done
