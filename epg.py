#!/usr/bin/python
import sys, time
import sqlite3
import mjd       # Modified Julian Date to tuple (y,m,d)
import time

ST_INIT     = 0
ST_EID      = 1 # Service_ID: 514 (0x0202)  [=  --> refers to PMT program_number] 
ST_START    = 2 # UTC
ST_DURATION = 3
ST_STATUS   = 4
ST_DESC77   = 5 # DVB-DescriptorTag: 77 (0x4d)  [= short_event_descriptor]
ST_DESC78   = 6 # DVB-DescriptorTag: 78 (0x4e)  [= extended_event_descriptor]
ST_DESC77_LEN = 7
ST_DESC78_LEN = 8
ST_DESC77_NAME = 9
ST_DESC77_NAME_LEN = 10
ST_DESC77_TEXT = 11
ST_DESC78_TEXT = 12

state = ST_INIT
state_name = "ST_INIT ST_EID ST_START ST_DURATION ST_STATUS ST_DESC77 ST_DESC78 ST_DESC77_LEN ST_DESC78_LEN ST_DESC77_NAME ST_DESC77_NAME_LEN ST_DESC77_TEXT ST_DESC78_TEXT "

#service state variables
service=0 # channel code - see scan commnad
start=0
duration=0
status=0
desc_short=""
desc_long=""
desc_short_len=0
desc_long_len=0
desc_name=""
desc_name_len=0
event_id=0

#decoding support variables
desc_short_len_last=0
desc_long_len_last=0

#decoding statistics
event_cnt=0

global connection
global nln

def stateInit():
  global state
  global service
  global start
  global duration
  global status
  global desc_short
  global desc_long
  global desc_short_len
  global desc_long_len
  global desc_name
  global desc_name_len
  global event_id
  global desc_short_len_last
  global desc_long_len_last

  service=0
  start=0
  duration=0
  status=0
  desc_short=""
  desc_long=""
  desc_short_len=0
  desc_long_len=0
  desc_name=""
  desc_name_len=0
  event_id=0
  desc_short_len_last=0
  desc_long_len_last=0

def stateName(state):
  global state_name
  state_cnt = 0
  state_pos = 0
  while state != state_cnt:
    state_pos = state_name.find(" ", state_pos+1)
    state_cnt = state_cnt + 1
  state_pos_end = state_name.find(" ", state_pos+1)
  return state_name[state_pos : state_pos_end]

def setState(state_new):
  global state
  #state_name = stateName(state)
  #state_name_new = stateName(state_new)
  #print state_name, "->", state_name_new
  state = state_new

def statePrint():
  print "event_id:", event_id
  print "service:", service
  print "desc_name_len", desc_name_len
  print "desc_name:", desc_name
  print "start:", start
  print "duration:", duration
  print "status:", status
  print "desc_short_len:", desc_short_len
  print "desc_short:", desc_short
  print "desc_long_len:", desc_long_len
  print "desc_long:", desc_long
  print "------------------------"

def ISO639_2ToUTF8(str):
  #return unicode(str, "iso-639-2").encode("utf-8")
  sout = ""
  for ch in str:
    #if ord(ch) < 0xC0:
    if ord(ch) < 0x80:
      sout = sout + ch
  #print sout
  return sout

def saveDB():
  global cursor

  global state
  global service
  global start
  global duration
  global status
  global desc_short
  global desc_long
  global desc_short_len
  global desc_long_len
  global desc_name
  global desc_name_len
  global event_id
  global desc_short_len_last
  global desc_long_len_last
  global event_cnt

  #save service name
  req = "SELECT * FROM SERVICE WHERE code==%d;"%(service)
  cursor.execute(req)
  row = cursor.fetchall()
  service_id = 0
  if len(row) == 0:
    cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [service, "0x%04x"%service])
    print service
    service_id = cursor.lastrowid
    #print "!A"
  else:
    (service_code, service_name) = row[0]
    if service_code == service:
      service_id = service_code
      #print "!B service(%s) found as %d"%(service_name, service_code)
    elif len(row) > 2:
      print "SERVICE rows!!", row
      exit()

  #req = "SELECT * FROM EPG WHERE event==%d and service_id==%d"%(event_id, service_id)
  req = "SELECT id FROM EPG WHERE service_id==%d and start_tm==%d and duration_tm==%d"%(service, start, duration)
  cursor.execute(req)
  row = cursor.fetchall()
  rows = len(row)
  if rows > 1:
    #delete duplicit rows
    for pos in range(2, rows):
      req="DELETE FROM EPG WHERE id==%d"%row[id][0]
  elif rows > 0:
    #do not save, aready known
    #(row_id , row_event, row_service_id, row_start_tm, row_duration_tm, row_name_id, row_sname_id, row_lname_id) = row[0]
    #print "ln(%d),event(%d),service(%d) found at(%d):"%(nln, event_id, service, row_id), row[0]
    return

  cursor.execute("INSERT INTO NAME VALUES (null, ?);", [ISO639_2ToUTF8(desc_name)])
  name_id = cursor.lastrowid

  cursor.execute("INSERT INTO SNAME VALUES (null, ?);", [ISO639_2ToUTF8(desc_short)])
  sname_id = cursor.lastrowid

  cursor.execute("INSERT INTO LNAME VALUES (null, ?);", [ISO639_2ToUTF8(desc_long)])
  lname_id = cursor.lastrowid

  recording = 0

  cursor.execute("INSERT INTO EPG VALUES (null, ?, ?, ?, ?, ?, ?, ?, ?);", [event_id, service_id, start, duration, name_id, sname_id, lname_id, recording])

  #print "ln:%d insert record(%d)"%(nln, lname_id) #, event_id, service_id, start, duration, name_id, sname_id, lname_id, recording

  global connection
  connection.commit()

def TagNum(tag, nextState, base=10):
  pos = ln.find(tag)
  if -1 != pos :
    setState(nextState)
    pos = pos + len(tag) + 1
    value = ln[pos : ln.find(" ", pos)]
    return (True, int(value, base))
  return (False, "")

def TagStr(tag, nextState):
  pos = ln.find(tag)
  if -1 != pos :
    setState(nextState)
    text = ln[pos + len(tag) + 1 : len(ln)]
    return (True, text)
  return (False, "")

def parse(ln):
  #print "ln: ", ln
  #time.sleep(1)

  global state
  global service
  global start
  global duration
  global status
  global desc_short
  global desc_long
  global desc_short_len
  global desc_long_len
  global desc_name
  global desc_name_len
  global event_id
  global desc_short_len_last
  global desc_long_len_last
  global event_cnt

  (found_eid, value) = TagNum("Event_ID:", ST_EID)
  if (found_eid == True):
    event_cnt = event_cnt + 1
    if desc_name == "":
      event_id = value
    else:
      #statePrint()
      saveDB()
      service_tmp = service  # save service number - we are inside a service block
      stateInit()
      event_id = value
      service = service_tmp
  else:
    (found_sid, value) = TagNum("Service_ID:", ST_EID)
    if (found_sid == True): 
      if desc_name == "":
        service = value
      else:
        #statePrint()
        saveDB()
        stateInit()
        service = value
        return

  if state == ST_EID:
    (found, mjd_start) = TagNum("Start_time:", ST_START, 16)
    if found:
      th = 10*((mjd_start & 0xF00000) >> 20) + ((mjd_start & 0x0F0000) >> 16)
      tm = 10*((mjd_start & 0x00F000) >> 12) + ((mjd_start & 0x000F00) >> 8)
      ts = 10*((mjd_start & 0x0000F0) >> 4) + (mjd_start & 0x00000F)
      (dy,dm,dd) = mjd.mjd2time((mjd_start & 0xFFFF000000) >> 24)
      start = time.mktime((dy,dm,dd,th,tm,ts,0,0,0)) - time.timezone

  elif state == ST_START:
    (found, duration) = TagNum("Duration:", ST_DURATION, 16)
    if found:
      th = 10*((duration & 0xF00000) >> 20) + ((duration & 0x0F0000) >> 16)
      tm = 10*((duration & 0x00F000) >> 12) + ((duration & 0x000F00) >> 8)
      ts = 10*((duration & 0x0000F0) >> 4) + (duration & 0x00000F)
      duration = ts + tm*60 + th*3600
      #print "duration:%d th:%d tm:%d ts:%d"%(duration,th,tm,ts)

  elif state == ST_DURATION:
    (found, status) = TagNum("Running_status:", ST_STATUS)

  elif state == ST_STATUS:
    (found, value) = TagNum("DVB-DescriptorTag:", ST_DESC77)
    if found == True:
      if (value == 78): setState(ST_DESC78)
      elif (value != 77): setState(ST_STATUS)


  elif state == ST_DESC77:
    (found, desc_name_len) = TagNum("event_name_length:", ST_DESC77_NAME_LEN)

  elif state == ST_DESC77_NAME_LEN:
    (found, value) = TagStr("event_name:", ST_DESC77_NAME)
    if found == True:
      desc_name = value[1 : desc_name_len+1]

  elif state == ST_DESC77_NAME:
    (found, value) = TagNum("text_length:", ST_DESC77_LEN)
    if found == True:
      desc_short_len_last = value
      desc_short_len = desc_short_len + desc_short_len_last

  elif state == ST_DESC78:
    (found, value) = TagNum("text_length:", ST_DESC78_LEN)
    if found == True:
      desc_long_len_last = value
      desc_long_len = desc_long_len + desc_long_len_last

  elif state == ST_DESC77_LEN:
    (found, value) = TagStr("text_char:", ST_DESC77_TEXT)
    if found == True:
      desc_short = desc_short + value[1 : desc_short_len_last+1]

  elif state == ST_DESC77_TEXT:
    (found, value) = TagStr("text_char:", ST_DESC77_TEXT)
    if found == True:
      desc_short = desc_short + value[1 : desc_short_len_last+1]
    else:
      (found, value) = TagStr("DVB-DescriptorTag: 78", ST_DESC78)
      if found == False:
        (found, value) = TagStr("Event_ID:", ST_EID)

  elif state == ST_DESC78_LEN:
    (found, value) = TagStr("text:", ST_DESC78_TEXT)
    if found == True:
      desc_long = desc_long + value[1 : desc_long_len_last+1]

  elif state == ST_DESC78_TEXT:
    (found, value) = TagStr("text_char:", ST_DESC78_TEXT)
    if found == True:
      desc_long = desc_long + value[1 : desc_long_len_last+1]
    else:
      (found, value) = TagStr("DVB-DescriptorTag: 78", ST_DESC78)
      if found == False:
        (found, value) = TagStr("DVB-DescriptorTag: 77", ST_DESC77)
        if found == False:
          (found, value) = TagStr("Event_ID:", ST_EID)

  return

if __name__ == "__main__":
  try:

    print "connecting epg.db"
    connection = sqlite3.connect('epg.db')
    cursor = connection.cursor()
    print "connected"

    print "read dvbsnoop data"
    nln=0
    while True:
      #print "ln:", nln
      nln = nln + 1
      ln = sys.stdin.readline()
      if ln=="": break
      #sys.stdout.write(ln)
      parse(ln)

    connection.commit()
    connection.close()
    print "event_cnt", event_cnt

  except:
    print "error %s: %s"%(sys.exc_info()[0], sys.exc_info()[1])
