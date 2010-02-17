from __future__ import with_statement
import time
import os
import signal
from epgScheduler import EpgScheduler
from schTime import RAWTimeToString, UTCTimeToString
import thread
import subprocess

# kill -s 10 epgRec_PID
def SIGUSR1_Handler(signum, stack):
  return

def SIGINT_Handler(signum, stack):
  print "Ctrl-C received, exit"
  global Exit
  Exit = True
  #signal.alarm(0)


if __name__ == "__main__":
  sch = EpgScheduler()
  lock = thread.allocate_lock()

  signal.signal(signal.SIGUSR1, SIGUSR1_Handler)
  signal.signal(signal.SIGINT, SIGINT_Handler)

  sch.CheckRunning()

  Exit=False
  while Exit == False:
    tmWait = int(sch.Reschedule())
    print "next Reschedule: %s"%UTCTimeToString(time.time()+tmWait)
    time.sleep(tmWait)
