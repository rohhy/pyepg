#!/bin/bash
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

#Input: free CPU time in seconds
#This script reencode all audio files to mp3 with 128kb bitrate
#Exit when finish or no free time

PWMODE=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)
echo "performance" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

DIR_SCRIPTS=/root/scripts
TIME_SEC="date +%s"
#echo $($TIME_SEC)

TIME_SLOT=$1
TIME_MIN=10*60
TIME_START=$($TIME_SEC)

DIR_MOVIEZ=/mnt/flash/moviez

#list audio files
FILES=$(ls "$DIR_MOVIEZ"/*.avi -la | grep CRo | tr -s " " | cut -d " " -f5,8 | grep -v 4096)
echo $(echo "$FILES" | wc -l)" files found"

#while files
echo "$FILES" | while read line; do
  if [ -z "$line" ]; then continue; fi
  SIZE=$(echo "$line" | cut -d " " -f1)
  FILE=$(echo "$line" | cut -d " " -f2)

  #estimate time
  TIME_EST=$(( $SIZE/(1024*1024) ))
  echo $($TIME_SEC)
  TIME_LEFT=$(( $TIME_START - $($TIME_SEC) + $TIME_SLOT - $TIME_MIN ))
  echo "$FILE Estimate: $TIME_EST, Left: $TIME_LEFT"
  if [ "$TIME_LEFT" -lt "$TIME_EST" ]; then
    echo "Skip file - not enough time left"
    continue
  fi

  #reencode
  lame -b 128 "$FILE" "$FILE".mp3

  #delete
  rm "$FILE"
done
echo "done"

echo "$PWMODE" > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
