#!/usr/local/bin/python
import sqlite3
import sys
import time
from schEvent import Event
import schDB

db = schDB.schDB()
for item in db.GetALL():
  event = Event(*item)
  print "%d: %s %s \"%s\""%(event.DBID, db.Service(event.service), event.ToString(), db.Name(event.name))
