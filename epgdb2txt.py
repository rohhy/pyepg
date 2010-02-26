#!/usr/local/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

import sqlite3
import sys
import time
from schEvent import Event
from epgdb import EpgDB

db = EpgDB()
for item in db.EpgAll():
  event = Event(*item)
  print "%d: %s %s \"%s\""%(event.DBID, db.Service(event.service), event.ToString(), db.Name(event.name))
