#!/usr/local/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

# TUNE="PRIMA,CT 1,Z1,CT1 (HD Test)"

import sqlite3
import sys

connection = sqlite3.connect('epg.db')
cursor = connection.cursor()
try:
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0101, "CT_1"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0102, "CT_2"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0103, "CT_24"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0104, "CT_4"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0202, "NOVA_CINEMA"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0201, "_NOVA"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0301, "PRIMA"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0302, "Prima_COOL"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0303, "Prima (MPEG-4 HD)"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0401, "Ocko"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0501, "Noe_TV"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0601, "PublicTV"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0701, "Z1"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0801, "BARRANDOV_TV"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x4101, "CRo1-Radiozurnal"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x4102, "CRo2-Praha"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x4103, "CRo3-Vltava"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x4104, "CRo_Radio_Wave"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x4105, "CRo_D-dur"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x4106, "CRo_Leonardo"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x4107, "CRo_Radio_Cesko"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x4301, "Proglas"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0001, "CT1 (HD Test)"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0002, "Nova (MPEG-4 HD)"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0003, "O2 Info (MPEG-2)"])
  cursor.execute("INSERT INTO SERVICE VALUES (?, ?);", [0x0004, "Test 4 (MPEG-2)"])

  connection.commit()
  connection.close()
except:
  print str(sys.exc_info())
  exit
