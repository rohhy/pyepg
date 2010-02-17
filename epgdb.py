#!/usr/bin/python
import sqlite3
import sys
import os
import time
from schTime import UTCTimeToString
from schEvent import Event

class EpgDB:

  def __init__(self, dbFileName):
    exists = os.path.exists(dbFileName)
    self.connection = sqlite3.connect(dbFileName)
    self.cursor = self.connection.cursor()

    if exists == False:
      self.Init()


  def __del__(self):
    self.Close()


  #Base database functions (open, close, check)
  #-----------------------------

  def __Error(self, message):
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


  #Create a new database or clean and init
  def Init(self):
    print "Init db"

    print "Remove all tables"
    self.__Remove()

    print "Create tables"
    self.__Create()

    print "Sucessfully Done"


  #Remove all tables from the database
  def __Remove(self):
    try:
      sql = "select name from sqlite_master where type='table';"
      self.cursor.execute(sql)
      data = self.cursor.fetchall()

      for tname in data:
        if tname[0] == u'sqlite_sequence' :
          continue
        sql = "DROP TABLE %s"%tname
        self.cursor.execute(sql)

    except:
      print str(sys.exc_info())
      exit


  #Cerate database
  def __Create(self):
    try:
      #epg database
      sql = "CREATE TABLE SERVICE (code, service TEXT)"
      self.cursor.execute(sql)

      sql = "CREATE TABLE NAME (id INTEGER PRIMARY KEY, name TEXT)"
      self.cursor.execute(sql)

      sql = "CREATE TABLE SNAME (id INTEGER PRIMARY KEY, sname TEXT)"
      self.cursor.execute(sql)

      sql = "CREATE TABLE LNAME (id INTEGER PRIMARY KEY, lname TEXT)"
      self.cursor.execute(sql)

      sql = "CREATE TABLE EPG (id INTEGER PRIMARY KEY, event INTEGER, service_id INTEGER, start_tm INTEGER, duration_tm INTEGER, name_id INTEGER, sname_id INTEGER, lname_id INTEGER, recording INTEGER)"
      self.cursor.execute(sql)

      self.connection.commit()
      self.connection.close()

      #favorites database
      sql = "CREATE TABLE FAVOURITES (id INTEGER PRIMARY KEY, regexp_id INTEGER)"
      self.cursor.execute(sql)

      sql = "CREATE TABLE FAVREGEXPS (id INTEGER PRIMARY KEY, regexp TEXT)"
      self.cursor.execute(sql)

    except:
      print str(sys.exc_info())
      exit


  #Close the database
  def Close(self):
    self.connection.close()
    return


  #Check database integrity
  def Check(self):
    print "Checking database integrity"

    print "Removing duplicit event"
    self.__RemoveDuplicitEvents()

    print "Removing fake services"
    self.__RemoveDuplicitServices()

    print "Done"


  #Check database integrity - Find and remove all duplicit Events
  def __RemoveDuplicitEvents(self):
    sql = "SELECT id,service_id,start_tm,duration_tm,count(*) FROM EPG GROUP BY service_id,start_tm,duration_tm HAVING count(*) > 1"
    try:
      self.cursor.execute(sql)
      dupls = self.cursor.fetchall()
      self.connection.commit()
    except:
      self.__Error("Duplicit event search, sql:%s"%sql)
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
      self.__Error("Duplicit event removing, sql:%s"%sql)
      return
    return


  #Check database integrity - Find and remove all duplicit services (CT1, CT2, NOVA...)
  def __RemoveDuplicitServices(self):
    sql = "SELECT * FROM SERVICE;"
    try:
      self.cursor.execute(sql)
      services = self.cursor.fetchall()
    except:
      self.__Error("List services, sql:%s"%sql)
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
        self.__Error("Serch service events, sql:%s"%sql)
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
          self.__Error("Remove service %s, sql:%s"%(service[1], sql))
          return

    self.connection.commit()
    return

  #Search database functions
  #-----------------------------

  def Epg(self, epg_id):
    sql = "select * from epg where id=%s"%epg_id
    self.cursor.execute(sql)
    epg = self.cursor.fetchall()
    if len(epg) == 0: raise Exception('SQL no results',sql)
    return epg[0][0]

  def Sname(self, sname_id):
    sql = "select sname from sname where id=%s"%sname_id
    self.cursor.execute(sql)
    sname = self.cursor.fetchall()
    if len(sname) == 0: raise Exception('SQL no results',sql)
    return sname[0][0]

  def Lname(self, lname_id):
    sql = "select lname from lname where id=%s"%lname_id
    self.cursor.execute(sql)
    lname = self.cursor.fetchall()
    if len(lname) == 0: raise Exception('SQL no results',sql)
    return lname[0][0]

  def Name(self, name_id):
    sql = "select name from name where id=%s"%name_id
    self.cursor.execute(sql)
    name = self.cursor.fetchall()
    if len(name) == 0: raise Exception('SQL no results',sql)
    return name[0][0]

  #convert service id to text
  def Service(self, service_id):
    sql = "SELECT service FROM SERVICE WHERE code=%d"%service_id
    self.cursor.execute(sql)
    service = self.cursor.fetchall()
    if len(service) == 0:
      return "0x%x"%service_id
    return service[0][0]

  def Favourites(self, fav_id):
    sql = "select regexp from favourites where id=%s"%fav_id
    self.cursor.execute(sql)
    fav = self.cursor.fetchall()
    if len(fav) == 0: raise Exception('SQL no results',sql)
    return fav[0][0]


  #Advanced search database functions
  #-----------------------------

  #Name table
  #Find event by name like form time
  def NameLike(self, name, from_tm = int(time.time())):
    res = []
    search = "%" + name + "%"
    sql = "select * from name where name like '%s' order by id"%search;
    try:
      self.cursor.execute(sql)
      events = self.cursor.fetchall()
      self.connection.commit()

      for (event_id, event_name) in events:
        epg = self.EpgByName(event_id)
        (epg_id, event, service_id, start_tm, duration_tm, name_id, sname_id, lname_id, recording) = epg
        if recording == 1: continue
        if from_tm > (start_tm + duration_tm): continue

        res.append(epg_id)
    except:
      self.Error("Error event listing, sql:%s"%sql)
      return
    return res

  #Epg table
  def EpgByName(self, epg_id):
    sql = "select * from epg where name_id=%s"%epg_id
    self.cursor.execute(sql)
    epg = self.cursor.fetchall()
    if len(epg) == 0: raise Exception('SQL no results',sql)
    return epg[0][0]

  def EpgRunningAll(self):
    sql = "SELECT * FROM EPG WHERE recording=%d"%Event.RUN
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  def EpgAll(self):
    sql = "SELECT * FROM EPG"
    self.cursor.execute(sql)
    epg = self.cursor.fetchall()
    if len(epg) == 0: raise Exception('SQL no results',sql)
    return epg

  def EpgSetState(self, id, state):
    sql = "UPDATE EPG SET recording=%d WHERE id=%d"%(state, id)
    self.cursor.execute(sql)
    self.connection.commit()
    return

  def EpgReadyAll(self, tmStart):
    if tmStart == 0:
      sql = "SELECT * FROM EPG WHERE start_tm+duration_tm > %d and recording=%d ORDER BY start_tm LIMIT 1"%(time.time(), Event.READY)
    else:
      sql = "SELECT * FROM EPG WHERE start_tm+duration_tm > %d and start_tm > %d and recording = %d ORDER BY start_tm LIMIT 1"%(time.time(), tmStart, Event.READY)
    self.cursor.execute(sql)
    return self.cursor.fetchall()

  #Favourites table
  def FavouritesAll(self):
    sql = "select regexp_id from favourites"
    self.cursor.execute(sql)
    fav = self.cursor.fetchall()
    if len(fav) == 0: raise Exception('SQL no results',sql)
    return fav[0]


  #Database facility support functions
  #-----------------------------

  def ReplaceDict(self, text, dic):
    for i, j in dic.iteritems():
      text = text.replace(i, j)
    return text

  #Format file name based on event name,date and service
  def FileName(self, epg_id):
    event = Event(*self.Epg(epg_id))

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
