#!/usr/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

import time
from schTime import UTCTimeToString, RAWTimeToString

class Event():
  #event type
  DISABLED = 0
  READY = 1
  RUN = 2
  DONE = 3
  FAILED = 4
  REMOVED = 5
  MISSED = 6

  def ToString(self):
    types = { 0:"DISABLED", 1:"READY", 2:"RUN", 3:"DONE", 4:"FAILED", 5:"REMOVED", 6:"MISSED" }
    return "%s, len %s, %s"%(UTCTimeToString(self.tmStart), RAWTimeToString(self.tmDuration), types[self.type])

  def __init__(self, id, event, service_id, start_tm, duration_tm, name_id, sname_id, lname_id, recording):
    self.type = recording          #DISABLED, READY, RUN, DONE, FAILED, REMOVED, MISSED
    self.tmStart = start_tm        #sec since 1900
    self.tmDuration = duration_tm  #sec relatve from tmStart
    self.eventID = id              #event id for dvbsnoop identification
    self.name = name_id            #text name to derive file name
    self.service = service_id      #channel
    self.DBID = id                 #to acess db
    self.pid = 0                   #recording process id
    self.fname = "unnamed"         #file name
