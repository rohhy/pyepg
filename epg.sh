#!/bin/sh
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

if [ -z "$1" ]; then echo "usage: $0 <dvb-num>"; exit; fi
echo "Using device $1 (of 2)"
DEVICE=$(( $1 - 1 ))

SCAN_RECORDS=4000 #2000 records is recomanded
DB_ARCHIVE=/mnt/flash
TM_START=$(date +"%s")

FINAL="epg.txt"
TUNE="PRIMA,CT 1,Z1,CT1 (HD Test)"
EPG=""
SCAN=""
TUNE_CNT=$(echo "$TUNE" | wc -l)
TUNE_POS=1

cp epg.db $DB_ARCHIVE/epg.$(/root/scripts/date.sh).db
#mv epg-plan.txt epg-plan.$(/root/scripts/date.sh).txt

echo "$TUNE" | tr "," "\n" | while read line; do
  echo "tune \"$line\" ($TUNE_POS of $TUNE_CNT)"
  #tzap -a1 -r -c /home/honza/.mplayer/channels.conf "$line" > /dev/null &
  #tzap -a0 -r -c /home/honza/.mplayer/channels.conf "$line" > /dev/null &
  tzap -a"$DEVICE" -r -c /home/honza/.mplayer/channels.conf "$line" > /dev/null &
  dvbsnoop -s sec -nph  -n "$SCAN_RECORDS" 0x12 | python epg.py

  TZAP_ID=$(ps aux | grep tzap | grep -v grep | tr -s " " | cut -d " " -f2)
  kill "$TZAP_ID"
  TUNE_POS=$(( TUNE_POS + 1 ))
done

#python epgdb2txt.py > epg.txt
python epgdbchk.py
