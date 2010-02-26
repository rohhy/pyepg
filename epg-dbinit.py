#!/usr/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

import sqlite3
import sys

connection = sqlite3.connect('epg.db')
cursor = connection.cursor()

print "remove all tables"
try:
  sql = "select name from sqlite_master where type='table';"
  cursor.execute(sql)
  data = cursor.fetchall()

  for tname in data:
    if tname[0] == u'sqlite_sequence' :
      continue
    sql = "DROP TABLE %s"%tname
    cursor.execute(sql)

except:
  print str(sys.exc_info())
  exit
print "done"

print "create new tables"
try:
  #tabulka service
  #sql = "CREATE TABLE SERVICE (code INTEGER PRIMARY KEY, service TEXT)"
  sql = "CREATE TABLE SERVICE (code, service TEXT)"
  cursor.execute(sql)

  #tabulka name
  sql = "CREATE TABLE NAME (id INTEGER PRIMARY KEY, name TEXT)"
  cursor.execute(sql)

  #tabulka short name
  sql = "CREATE TABLE SNAME (id INTEGER PRIMARY KEY, sname TEXT)"
  cursor.execute(sql)

  #tabulka long name
  sql = "CREATE TABLE LNAME (id INTEGER PRIMARY KEY, lname TEXT)"
  cursor.execute(sql)

  #tabulka epg
  sql = "CREATE TABLE EPG (id INTEGER PRIMARY KEY, event INTEGER, service_id INTEGER, start_tm INTEGER, duration_tm INTEGER, name_id INTEGER, sname_id INTEGER, lname_id INTEGER, recording INTEGER)"
  cursor.execute(sql)

  # #sql = "INSERT INTO Settings (setting, value) VALUES ('display_molecule_name', 'True')"
  #
  # #sql = "UPDATE Settings SET value=15 WHERE setting='slideshow_delay'"
  #
  # #sql = "DELETE FROM Settings WHERE id=1"
  #
  # #sql = "SELECT setting, id, value" 
  #
  # #data = cursor.fetchall()

  connection.commit()
  connection.close()
except:
  print str(sys.exc_info())
  exit

print "done"
