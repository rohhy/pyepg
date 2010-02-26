#!/usr/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

import sqlite3
import sys
import time

connection = sqlite3.connect('epg.db')
cursor = connection.cursor()

try:
  start = time.time() - 4*3600 + time.timezone
  sql = "SELECT * FROM EPG WHERE recording==1 and start_tm>%d ORDER BY start_tm"%start
  cursor.execute(sql)
  epg = cursor.fetchall()

  for item in epg:
    (id, event, service_id, start_tm, duration_tm, name_id, sname_id, lname_id, recording) = item
    #print "id, event, service_id, start_tm, duration_tm, name_id, sname_id, lname_id, recording"
    #print id, event, service_id, start_tm, duration_tm, name_id, sname_id, lname_id, recording

    sql = "SELECT * FROM SERVICE WHERE code==%d;"%service_id
    cursor.execute(sql)
    service = cursor.fetchall()[0][1]
    cursor.execute(sql)

    sql = "SELECT name FROM NAME WHERE id==%d;"%name_id
    cursor.execute(sql)
    name = cursor.fetchall()[0][0]
    #print "name: %s"%name

    start =  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_tm))
    duration = time.strftime("%H:%M:%S", time.gmtime(duration_tm))

    print "*\"%s\" %s %s 0 \"%s\""%(service, start, duration, name)
    #exit()

  connection.close()
except:
  print str(sys.exc_info())
  exit
