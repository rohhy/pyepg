#!/usr/local/bin/python
import sqlite3
import sys
import time

connection = sqlite3.connect('epg.db')
cursor = connection.cursor()

try:
  sql = "SELECT * FROM EPG ORDER BY service_id, start_tm"
  cursor.execute(sql)
  epg = cursor.fetchall()

  for item in epg:
    (id, event, service_id, start_tm, duration_tm, name_id, sname_id, lname_id) = item
    #print "id, event, service_id, start_tm, duration_tm, name_id, sname_id, lname_id"
    #print id, event, service_id, start_tm, duration_tm, name_id, sname_id, lname_id

    sql = "SELECT * FROM SERVICE WHERE code==%d;"%service_id
    cursor.execute(sql)
    row = cursor.fetchall()
    if len(row) != 1:
      service = "0x%04d"%service_id
    else:
      service = row[0][1]
      #print "service: %s"%service
      cursor.execute(sql)
      #print cursor.fetchall()

    sql = "SELECT name FROM NAME WHERE id==%d;"%name_id
    cursor.execute(sql)
    name = cursor.fetchall()[0][0]
    #print "name: %s"%name

    (dy,dm,dd, th,tm,ts, a,b,c) = time.gmtime(start_tm)
    th = th + 3
    if th >= 24: th = th - 24
    start =  time.strftime("%Y-%m-%d %H:%M:%S", (dy,dm,dd, th,tm,ts, a,b,c))
    (a,b,c,uh,um,us,d,e,f) = time.gmtime(duration_tm)

    uh = uh + 1
    if uh >= 24: uh = uh - 24
    duration = time.strftime("%H:%M:%S", (0,0,0,uh,um,us,0,0,0))

    print "\"%s\" %s %s 0 \"%s\""%(service, start, duration, name)
    #exit()

  connection.close()
except:
  print str(sys.exc_info())
  exit
