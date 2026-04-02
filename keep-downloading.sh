#!/usr/bin/env bash
#
# Usage: nohup ./keep-downloading.sh &
#
# A script that keeps calling 'main.py' sith 4 downloads,
# pausing for 8 minutes between each attempt.
# Messages are written (appended) to 'keep-downloading.log'
# and the downloads written to './tmp' (which is wiped before each run).
#
# This was designed for #1978 to investigate download speeds
# over long periods of time in order to try and identify a pattern
# (if any) where downloads would 'slow down'.

cmd="uv run main.py 4 --verbose"
log="keep-downloading.log"
delay="8m"
# The default download directory.
# Be VERY careful - we wipe it so it MUST be local.
# This is not completely safe but it must start with '.'.
download_directory="/tmp"

if  [[ ! $download_directory == .* ]] ;
then
    echo "ERROR: Download directory must start with '.' (it cannot be $download_directory)"
    exit 1
fi

download=1
while true
do
  echo $(date '+%Y-%m-%d %H:%M') Wiping: ${dst}
  rm -rf ${download_directory}
  echo $(date '+%Y-%m-%d %H:%M') Downloading: ${download} >> ${log}
  $cmd >> ${log} 2>&1
  echo $(date '+%Y-%m-%d %H:%M') Sleeping ${delay} ... >> ${log}
  sleep ${delay}
  echo --- >> ${log}
  ((download++))
done
