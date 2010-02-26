#!/bin/bash
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

if [ -z "$1" -o -z "$2" ]; then echo "usage: $0 <pid> <file name>"; exit 1; fi
RECPID="$1"
FOUT="$2"

DIR_SCRIPTS=/root/scripts
DIR_REC=/mnt/flash/rec
DIR_ARCH=/mnt/flash/moviez

echo "killing $RECPID"
kill -9 "$RECPID"
mv "$DIR_REC/$FOUT" "$DIR_ARCH/$FOUT"

REC_CNT=$(ps aux | egrep "mplayer|mencoder" | grep -v grep)
if [ -z "$REC_CNT" ]; then
  "$DIR_SCRIPTS"/cpu-powersave.sh
fi
