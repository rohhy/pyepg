#!/bin/bash
if [ -z "$1" -o -z "$2" -o -z "$3" -o -z "$4" ]; then
  echo "usage: $0 <adapter> <service> <sec> <file name>"
  echo "example: StartRec.sh 2 \"CT 1\" 20 ct1.avi"
  exit 1
fi

ADAPTER="$1" 
SERVICE="$2" 
SEC="$3"
FOUT="$4"

DIR_SCRIPTS="/root/scripts"
PID=0

#PIDS_OLD=$(./findpids.sh "mencoder mplayer")

"$DIR_SCRIPTS"/cpu-performance.sh

CH="dvb://$ADAPTER@$SERVICE"
#OPT="-endpos $SEC -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=1024:v4mv:vhq=4 -oac mp3lame -lameopts abr:br=128:aq=0:mode=1 -o $FOUT"
OPT="-quiet -endpos $SEC -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=1024 -oac mp3lame -lameopts abr:br=128:aq=0:mode=1 -o $FOUT"

echo "CMD: mencoder $CH $OPT" 1>&2
#MEN_OUT=""
mencoder "$CH" $OPT 2>&1 &
#MEN_OUT=$(mencoder "$CH" $OPT 2>&1 > /dev/null &)
#echo "MEN_OUT: $MEN_OUT" 1>&2

ERR_VO=$(echo "$MEN_OUT" | grep "Video stream is mandatory!")
if [ -n "$ERR_VO" ]; then
  mplayer -dumpstream "$CH" -dumpfile "$FOUT" &
fi

#return current mecoder/mplayer PID
#PIDS=$(./findpids.sh "mencoder mplayer")
#echo "PIDS_OLD: $PIDS_OLD"
#echo "PIDS: $PIDS"
#echo "PID: $(./cmplst.sh "$PIDS_OLD" "$PIDS")"
