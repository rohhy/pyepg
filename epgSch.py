from schEvent import Event
from schStack import EventStack
from epgdb import epgdb
from schTime import UTCTimeToString 
import time
import os
import subprocess
import sys
import shutil

class EpgScheduler:
  def __init__(self):
    self.stack = EventStack()
    self.db = EpgDB()
    self.cardUsed = 0

    self.cardCount = 2
    self.dirRec="/mnt/flash/rec"
    self.dirArch="/mnt/flash/moviez"
    self.IDLE_TIME = 3600*24
    self.tmBefore = 10*60
    self.tmAfter = 10*60
    self.tmIndex = 2*60

  def __del__(self):
    print "EpgScheduler Exit"
    for event in self.stack.stack:
      if event.type == event.RUN:
        print "kill recording pid: %s"%event.pid
        try:
          os.kill(event.pid, 9)
        except:
          print "PID %d not found"%event.pid
          print "Details: ", sys.exc_info()

        time.sleep(3)

        spath = self.dirRec +"/"+ event.fname
        tpath = self.dirArch +"/"+ event.fname
        print "move %s -> %s"%(spath, tpath)
        try:
          shutil.move(spath, tpath)
        except :
          print "File %s not found"
          print "Details: ", sys.exc_info()


  #Find all RUNning events in the DB
  #Check validity and start recording
  def CheckRunning(self):
    print "Checking running ..."
    res = self.db.EpgRunningAll()
    if len(res) > 0:
      print "total %d runnings found"%len(res)
      runCnt = 0
      for res_ in res:
        event = Event(*res_)
        print "%d: running found: %s"%(runCnt, event.ToString())
        if event.tmStart < time.time() and event.tmStart + event.tmDuration > time.time():
          print "%d: activate: %s"%(runCnt, event.ToString())
          if self.cardUsed >= self.cardCount:
            print "%d: Recording failed (3), no free recording device"%runCnt
            continue
          self.db.EpgSetState(event.DBID, Event.RUN)
          event.type = event.RUN
          self.stack.Add(event)
          self.StartRec(event)
        else:
          print "%d: set db as failed: %s"%(runCnt, event.ToString())
          self.db.EpgSetState(event.DBID, Event.FAILED)
        runCnt = runCnt +1
    return


  #search the DB for a new event before the Event.READY on the self.stack
  def Reschedule(self):
    print "---------------------"
    print "Rechedule, time: %d (%s)"%(time.time(), UTCTimeToString(time.time()))
    print "Start, stack:\n%s"%self.stack.ToString()

    tmWait = self.IDLE_TIME
    readyDB = -1
    readyStack = -1

    res = self.db.EpgReadyAll(0)                               # najdi prvni READY nebo RUN v DB
    if len(res) > 0:
      readyDB = Event(*res[0])
      print "readyDB: %s"%(readyDB.ToString())

      tm = time.time() - readyDB.tmStart - self.tmBefore
      print "(!1) tm %d"%tm
      if tm < 0: tm = readyDB.tmStart + readyDB.tmDuration + self.tmAfter
      print "(!1-2) tm %d"%tm
      if tmWait>tm:
        tmWait = tm
        print "(1)NEW tmWait:%s"%UTCTimeToString(time.time()+tmWait)

    #projdi stack
    stackPos = 0
    failedPos = 0
    while stackPos < len(self.stack.stack):
      event = self.stack.stack[stackPos]
      eventDB = Event(*self.db.Epg(event.DBID))
      tm = event.tmStart - time.time()
      print "tm1 tm:%s"%UTCTimeToString(time.time()+tm)

      print "%d: Stack: %s"%(stackPos, event.ToString())
      print "%d: DB: %s"%(stackPos, eventDB.ToString())

      if eventDB.type != Event.READY:                      #  vsechny !READY
        if eventDB.type == Event.RUN:
          tmRun = tm + event.tmDuration + self.tmAfter     #  RUN
          if tmRun > 0:
            print "%d: runing is OK"%stackPos
            if tmWait>tmRun:
              print "tm2 tm:%s"%UTCTimeToString(time.time()+tm)
              tmWait = tmRun
              print "%d: (2)NEW tmWait: %d"%(stackPos, tmWait)
            stackPos = stackPos +1
            continue

        print "%d: RUN deactivated, removed"%stackPos      #  !READY and RUN -> FINISHED 
        if event.type == event.RUN:
          self.StopRec(event)
          if failedPos > 0: stackPos = failedPos           #  retry when RUN found and failed
        self.stack.Del(event)
        self.db.EpgSetState(event.DBID, event.DONE)
        #stackPos = stackPos +1                            #  do not increment position, stack cutted
        continue

      else:                                                #  READY
        if event.DBID != readyDB.DBID:                     #  DB priority is higher
          self.stack.Del(event)
          print "%d: READY not actual, remove"%stackPos
          stackPos = stackPos +1
          continue
        if tm - self.tmBefore <= 0:                        #   READY -> RUN
          if self.cardUsed >= self.cardCount:              #     no device
            #self.db.EpgSetState(event.DBID, event.FAILED)    #     keep READY, RUN when device released
            print "%d: recording failed (1), no device"%stackPos
            failedPos = stackPos
          else:
            print "%d: READY -> RUN"%stackPos
            self.db.EpgSetState(readyDB.DBID, Event.RUN)
            event.type = event.RUN
            self.StartRec(event)
            tm = tm + event.tmDuration + self.tmAfter
            print "tm3 tm:%s"%UTCTimeToString(time.time()+tm)
        else:                                              #  READY is waiting
          if readyStack == -1:                             #    first READY found
            print "%d: the READY found"%stackPos
            readyStack = event
            tm = tm - self.tmBefore
          else:                                            #    remove READY, only one at all on the stack
            print "%d: spare record (2), remove"%stackPos
            self.stack.Del(event)
            #stackPos = stackPos +1                        #    do not increment position, stack cutted
            continue

      if tm>0 and tmWait>tm:
        tmWait = tm
        print "%d: (3)NEW tmWait: %s"%(stackPos, UTCTimeToString(time.time()+tmWait))
      print "tmWait%s"%UTCTimeToString(time.time()+tmWait)
      stackPos = stackPos +1

    #end projdi stack

    # I.) pokud je reday je v db i na stacku
    #   stack a databaze je konzistantni
    # II.) pokud ready neni na stacku ale je v db, pridam na stack, mam ho
    #   ready byl vyrazen, musim jej nahradit z db
    # III.) pokud ready je na stacku ale neni to jako ten v db, zmenil se stav v db
    #   logicky se vylucuje s radkou: pokud stavDB != ready
    # IV.) pokud neni na stacku ani v db
    #   mam smulu, vracim -1

    if readyStack == -1:                               #  no READY found, search DB
      print "No READY found, search DB"
      print "stack:\n %s"%self.stack.ToString()
      dbPos = 0

      found = False
      while found == False and readyDB != -1:          #  search DB loop
        dbPos = dbPos + 1
        tm = readyDB.tmStart - time.time()
        print "tm4 tm:%s"%UTCTimeToString(time.time()+tm)

        isRunning = False                              #  RUN or READY found
        for stackPos in range(0, len(self.stack.stack)):
          if self.stack.stack[stackPos].DBID == readyDB.DBID:
            print "db%d: already RUN, skip"%dbPos
            isRunning = True
            break

        if isRunning == False:                         #  READY found
          if tm - self.tmBefore <= 0:                  #  READY -> RUN
            print "db%d:a new running found in DB"%dbPos
            if self.cardUsed >= self.cardCount:
              print "%d: Recording failed (2), no device"%dbPos
              break
            print "%d: READY -> RUN"%stackPos
            self.db.EpgSetState(readyDB.DBID, Event.RUN)
            readyDB.type = Event.RUN
            self.stack.Add(readyDB)
            self.StartRec(readyDB)
            tm = tm + readyDB.tmDuration + self.tmAfter
            print "tm5 tm:%s"%UTCTimeToString(time.time()+tm)
          else:                                        #  READY, done
            found = True
            readyStack = readyDB
            self.stack.Add(readyDB)
            tm = tm - self.tmBefore
            print "tm6 tm:%s"%UTCTimeToString(time.time()+tm)

        if tm>0 and tmWait>tm:                         #  update tmWait
          tmWait = tm
          print "(4)NEW tmWait:%s"%UTCTimeToString(time.time()+tmWait)
        print "tmWait%s"%UTCTimeToString(time.time()+tmWait)

        if found == False:                             #  search next READY form the DB
          res = self.db.EpgReadyAll(readyDB.tmStart)
          if len(res) == 0: readyDB = -1
          else:
            readyDB = Event(*res[0])

    #end search DB
    print "Exit, stack:\n%s"%self.stack.ToString()
    return tmWait


  #start recording
  def StartRec(self, event):
    #todo: tzap tune channel, wait while dvbsnoop on channel do not detect program is running

    self.cardUsed = self.cardUsed + 1
    print "StartRec: starting a recording: %s"%event.ToString()

    dev = self.cardUsed

    #calculate recording time
    lensec = event.tmDuration
    if event.tmStart > time.time():                 #program didn't start => plus time before start
      lensec = lensec + event.tmStart - time.time()
    else:                                           #program is running => minus time running
      lensec = lensec - (time.time() - event.tmStart)
    lensec = lensec + self.tmAfter - self.tmIndex   #plus time after, minus time to index avi file

    fname = self.db.FileName(event.DBID) + ".avi"
    if os.path.exists(self.dirRec + "/" + fname) or os.path.exists(self.dirArch + "/" + fname):
      cntName = 0
      while os.path.exists(self.dirArch + "/" + fname):
        fname = self.db.FileName(event.DBID) + ".%03d.avi"%cntName
        cntName = cntName + 1
    event.fname = fname

    service = self.db.Service(event.service)
    serviceDic= {'_':' '}
    service = self.db.ReplaceDict(service, serviceDic)

    #start rec
    recCmd="./StartRec.sh %d \"%s\" %d \"%s\" | grep PID: | cut -d \" \" -f2"%(dev, service, lensec, self.dirRec +"/"+ fname)
    print "StartRec cmd: %s"%recCmd
    procRec = subprocess.Popen(recCmd, stdout=subprocess.PIPE, shell=True)
    cmdPid = "ps aux"

    time.sleep(1)
    pid=0 
    procPid = subprocess.Popen(["ps", "aux"], stdout=subprocess.PIPE)
    pidOut = procPid.communicate()[0]
    pidLst = pidOut.split("\n")
    for pidLn in pidLst:
      if pidLn.find(service)!=-1 and pidLn.find("/bin/sh -c")==-1:
        #print "pid found: %s"%pidLn
        pid = int(pidLn.split(None)[1])
        break

    print "pidNew: %d"%pid
    if pid == 0:
      #event.type = event.FAILED
      return False

    event.pid = int(pid)
    event.type = event.RUN
    return True


  #stop recording
  def StopRec(self, event):
    self.cardUsed = self.cardUsed - 1
    print "StopRec: stop a recording: %s"%event.ToString()
    cmdStop = "./StopRec.sh %d %s"%(event.pid, event.fname)
    print "cmdStop: %s"%cmdStop
    os.system(cmdStop)
