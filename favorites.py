#!/usr/local/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

import epgdb

if __name__ == '__main__':
  db = EpgDB('epg.db')
  epgs = db.FindNameLike('Retro')

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
