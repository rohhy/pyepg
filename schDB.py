#!/usr/bin/python
import sys
import sqlite3
import time
from schTime import UTCTimeToString
from schEvent import Event

# list column names: PRAGMA table_info(EPG);
# add new column: ALTER TABLE EPG ADD state INTEGER;
# state column nebude pouzivan, misto nej bude slouzit recording column

class schDB:

  def __init__(self):
    self.connection = sqlite3.connect('epg.db')
    self.cursor = self.connection.cursor()
    return    

  def __del__(self):
    self.Close()

  def Close(self):
    self.connection.close()
    return

  def GetRunning(self):
    sql = "SELECT * FROM EPG WHERE recording=%d"%Event.RUN
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def GetALL(self):
    sql = "SELECT * FROM EPG"
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def GetID(self, _id):
    sql = "SELECT * FROM EPG WHERE id=%d"%_id
    self.cursor.execute(sql)
    return self.cursor.fetchall()[0]

  def GetReady(self, tmStart):
    if tmStart == 0:
      sql = "SELECT * FROM EPG WHERE start_tm+duration_tm > %d and recording=%d ORDER BY start_tm LIMIT 1"%(time.time(), Event.READY)
    else:
      sql = "SELECT * FROM EPG WHERE start_tm+duration_tm > %d and start_tm > %d and recording = %d ORDER BY start_tm LIMIT 1"%(time.time(), tmStart, Event.READY)
    #print "sql: %s"%sql
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def SetState(self, id, state):
    sql = "UPDATE EPG SET recording=%d WHERE id=%d"%(state, id)
    #print sql
    self.cursor.execute(sql)
    self.connection.commit()
    return

  #convert service id to text
  def Service(self, service_id):
    sql = "SELECT service FROM SERVICE WHERE code=%d"%service_id
    #print "sql: %s"%sql
    self.cursor.execute(sql)
    service = self.cursor.fetchall()
    if len(service) == 0:
      #raise Exception('SQL request failed',sql)
      return "0x%x"%service_id
    return service[0][0]

  def ReplaceDict(self, text, dic):
    for i, j in dic.iteritems():
      text = text.replace(i, j)
    return text

  #convert event name id to text
  def Name(self, name_id):
    sql = "SELECT name FROM NAME WHERE id=%d"%name_id
    #print "sql: %s"%sql
    self.cursor.execute(sql)
    name = self.cursor.fetchall()
    if len(name) == 0: raise Exception('SQL request failed',sql)
    return name[0][0]

  #format file name based on event name,date and service
  def FileName(self, epg_id):
    event = Event(*self.GetID(epg_id))

    service = self.Service(event.service)
    name = self.Name(event.name)

    tm = UTCTimeToString(event.tmStart)
    print "schDB: tm: \'%s\'"%tm
    tmDict = {" ":"-"}
    tmStart = self.ReplaceDict(tm, tmDict)

    nameDict = {' ':'-', '(':'-', ')':'_', ',':'_', '?':''}
    name = self.ReplaceDict(name, nameDict) 

    serviceDict = {' ':'-'}
    service = self.ReplaceDict(service, serviceDict)

    fname="%s_%s_%s"%(service, tmStart, name)
    return fname
