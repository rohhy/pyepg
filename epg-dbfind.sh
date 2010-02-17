#!/usr/bin/python
import sqlite3
import sys
import time
import traceback
import schTime
import time

class EpgDBFind:
  def __init__(self, dbFileName):
    self.connection = sqlite3.connect(dbFileName)
    self.cursor = self.connection.cursor()

  def __del__(self):
    self.connection.close()

  def Error(self, message):
    print "----------"
    print "ERROR: %s"%message
    #print str(sys.exc_info())

    print 'Caught: sys.exc_type =', sys.exc_type, 'sys.exc_value =', sys.exc_value
    print 'sys.exc_traceback =', sys.exc_traceback
    print sys.exc_info()
    print ".........."

    maxTBlevel=5
    #print formatExceptionInfo()
    # def formatExceptionInfo(maxTBlevel=5):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
      excArgs = exc.__dict__["args"]
    except KeyError:
      excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    #return (excName, excArgs, excTb)
    print (excName, excArgs, excTb)

  def Epg(self, epg_id):
    sql = "select * from epg where id=%s"%epg_id
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def EpgByName(self, epg_id):
    sql = "select * from epg where name_id=%s"%epg_id
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def Sname(self, sname_id):
    sql = "select sname from sname where id=%s"%sname_id
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def Lname(self, lname_id):
    sql = "select lname from lname where id=%s"%lname_id
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def Name(self, name_id):
    sql = "select name from name where id=%s"%name_id
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def Find(self, name):
    #print "Search %s"%name
    res = []
    time_now = int(time.time())
    search = "%" + name + "%"
    sql = "select * from name where name like '%s' order by id"%search;
    try:
      self.cursor.execute(sql)
      events = self.cursor.fetchall()
      self.connection.commit()

      for (event_id, event_name) in events:
        result = self.EpgByName(event_id)
        if len(result) == 0: continue
        (epg_id, event, service_id, start_tm, duration_tm, name_id, sname_id, lname_id, recording) = result[0]
        if recording == 1: continue
        if time_now > (start_tm + duration_tm): continue

        res.append(epg_id)
    except:
      self.Error("Error event listing, sql:%s"%sql)
      return
    print "Done"
    return res

if __name__ == '__main__':
  db = EpgDBFind('epg.db')
  epgs = db.Find('Retro')

  for event_id in epgs:
    result = db.Epg(event_id)
    if len(result) == 0: continue
    (epg_id, event, service_id, start_tm, duration_tm, name_id, sname_id, lname_id, recording) = result[0]

    name = ""
    result = db.Name(name_id)
    if len(result) == 0:
      name = "name_id=%s"%name_id
    else:
      name = result[0][0]

    sname = ""
    result = db.Sname(sname_id)
    if len(result) == 0:
      sname = "sname_id=%s"%sname_id
    else:
      sname = result[0][0]

    lname = ""
    result = db.Lname(lname_id)
    if len(result) == 0:
      lname = "lname_id=%s"%lname_id
    else:
      lname = result[0][0]

    print "%s \"%s\" \"%s\" \"%s\""%(schTime.UTCTimeToString(start_tm), name, sname, lname)
