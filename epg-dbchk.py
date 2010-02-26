#!/usr/bin/python
import sqlite3
import sys
import time
import traceback

class EpgDBChk:
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


  def RemoveDuplicitEvents(self):
    print "Removing duplicit event"
    sql = "SELECT id,service_id,start_tm,duration_tm,count(*) FROM EPG GROUP BY service_id,start_tm,duration_tm HAVING count(*) > 1"
    try:
      self.cursor.execute(sql)
      dupls = self.cursor.fetchall()
      self.connection.commit()
    except:
      self.Error("Duplicit event search, sql:%s"%sql)
      return

    print "%d Duplicit events found"%len(dupls)
    sql=""
    try:
      for dupl in dupls:
        (id, service_id, start_tm, duration_tm,cnt) = dupl
        sql = "DELETE FROM EPG WHERE service_id==%d AND start_tm==%d AND duration_tm==%d AND id!=%d;"%(service_id, start_tm, duration_tm, id)
        self.cursor.execute(sql)
        self.connection.commit()
    except:
      self.Error("Duplicit event removing, sql:%s"%sql)
      return
    print "Done"
    return


  def RemoveDuplicitServices(self):
    print "Removing fake services"
    sql = "SELECT * FROM SERVICE;"
    try:
      self.cursor.execute(sql)
      services = self.cursor.fetchall()
    except:
      self.Error("List services, sql:%s"%sql)
      return

    if len(services) > 0:
      print "%d services found"%len(services)

    for service in services:
      eventsCnt = 0
      sql = "SELECT * FROM EPG WHERE service_id==%d;"%service[0]
      try:
        self.cursor.execute(sql)
        events = self.cursor.fetchall()
        eventsCnt = len(events)
      except:
        self.Error("Serch service events, sql:%s"%sql)
        return

      if eventsCnt < 100:
        print "suspicious service %s(=%d), only %d events."%(service[1], service[0], eventsCnt)

        #remove events and service
        print "Remove service %s"%service[1]
        try:
          sql = "DELETE FROM EPG WHERE service_id==%d;"%service[0]
          self.cursor.execute(sql)

          sql = "DELETE FROM SERVICE WHERE code==%d;"%service[0]
          self.cursor.execute(sql)
        except:
          self.Error("Remove service %s, sql:%s"%(service[1], sql))
          return

    self.connection.commit()
    print "Done"
    return

if __name__ == '__main__':
  chk = EpgDBChk('epg.db')
  chk.RemoveDuplicitEvents()
  chk.RemoveDuplicitServices()
