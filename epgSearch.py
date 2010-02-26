#!/usr/local/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

import epgdb
import schTime
import sys


def find(text):
  db = epgdb.EpgDB()
  epgs = db.Like(text)

  if len(epgs) == 0:
    return "No events found."

  sout = "Found %d events."%len(epgs)

  for event_id in epgs:
    result = db.Epg(event_id)
    if len(result) == 0: continue
    (epg_id, event, service_id, start_tm, duration_tm, name_id, sname_id, lname_id, recording) = result

    service = db.ServiceName(service_id)
    if len(service) == 0:
      service = "service_id=%d"%service_id

    name = db.Name(name_id)
    if len(name) == 0:
      name = "name_id=%d"%name_id

    sname = db.Sname(sname_id)
    if len(sname) == 0:
      sname = "sname_id=%d"%sname_id

    lname = db.Lname(lname_id)
    if len(lname) == 0:
      lname = "lname_id=%d"%lname_id

    sout += "%s \"%s\" \"%s\" \"%s\" \"%s\"\n"%(schTime.UTCTimeToString(start_tm), service, name, sname, lname)
    sout += "----------------------------------------\n"

  return sout

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print "usage: python %s <name>"%sys.argv[0]
    sys.exit()

  #search
  text = sys.argv[1]
  print find(text)
