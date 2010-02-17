#!/bin/sh
SCAN_RECORDS=4000 #2000 records is recomanded

TM_START=$(date +"%s")

FINAL="epg.txt"
TUNE="PRIMA,CT 1,Z1,CT1 (HD Test)"
EPG=""
SCAN=""
TUNE_CNT=$(echo "$TUNE" | wc -l)
TUNE_POS=1

#mv epg.db epg.$(/root/scripts/date.sh).db
cp epg.db epg.$(/root/scripts/date.sh).db
#mv epg.txt epg.$(/root/scripts/date.sh).txt
mv epg-plan.txt epg-plan.$(/root/scripts/date.sh).txt
#python epg-dbinit.py
#python epg-service.py

echo "$TUNE" | tr "," "\n" | while read line; do
  echo "tune \"$line\" ($TUNE_POS of $TUNE_CNT)"
  #tzap -a1 -r -c /home/honza/.mplayer/channels.conf "$line" > /dev/null &
  tzap -a0 -r -c /home/honza/.mplayer/channels.conf "$line" > /dev/null &
  #EPG="$EPG"$(dvbsnoop -s sec -nph  -n "$SCAN_RECORDS" 0x12)
  #SCAN="$SCAN"$(scan -c | grep '(0x' | tr '\n' '~' | tr -s '\n' | tr -s " " | t$
  dvbsnoop -s sec -nph  -n "$SCAN_RECORDS" 0x12 | python epg.py

  TZAP_ID=$(ps aux | grep tzap | grep -v grep | tr -s " " | cut -d " " -f2)
  kill "$TZAP_ID"
  TUNE_POS=$(( TUNE_POS + 1 ))
done

python epg-txt.py > epg.txt
