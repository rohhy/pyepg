#!/usr/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

# epg search
import os
import epgSearch
from epgdb import EpgDB
import epgSearch
import time
from os import system

class epgWebSearch:
  def __init__(self):
    self.db = EpgDB()
    self.cardsCount = 2
    return

  # parse post parameters
  def parsePost(self, data, setrec, rmrec):
    findName = ""

    for mini in data:
      #print "name:%s value:%s"%(mini.name, mini.value)

      service=""
      start=0

      if mini.name == "find":
        findName = mini.value
      elif mini.name == "epgset":
        delim = mini.value.find(".")
        service = mini.value[0 : delim]
        start = mini.value[delim+1 : len(mini.value)]
        start = int(start)

        #pokud je v rmrec, tak ji pouze vyjmi
        found = False
        for item in rmrec:
          if start == item:
            found = True
            rmrec.remove(start)
            break
        if found == False:
          #pridej do setrec pokud neni v rmrec (= byla uvedena jako epgpreset ale nebyla jeste nalezena epgset)
          for item in setrec:
            if start == item:
              found = True
              break
          if found == False:
            setrec.append(start)

      elif mini.name == "epgpreset":
        delim = mini.value.find(".")
        service = mini.value[0 : delim]
        start = mini.value[delim+1 : len(mini.value)]
        start = int(start)

        #pokud je v setrec, tak ji pouze vyjmi
        found = False
        for item in setrec:
          if start == item:
            found = True
            setrec.remove(start)
            break
        if found == False:
          for item in setrec:
            if start == item:
              found = True
              break
          if found == False:
            rmrec.append(start)

    return (findName, setrec, rmrec)


  #search for conflicts
  def conflicts(self, start, duration, recording, name_id):
    #print "start:%d, duration:%d, recording:%d"%(start, duration, recording)

    conflictInfo = ""
    conflictMark = "&nbsp"
    conflicts = self.db.EpgConflicts(name_id, start, duration)

    clen = len(conflicts)
    if clen > 1:
      conflictMark = "!"

      #generate more detail info when remove a program is required
      if clen+1 > self.cardsCount:
        conflictInfo = conflictInfo + "<BLOCKQUOTE>%d conflics found, remove %d recording<BR>\n"%(clen, clen+1-self.cardsCount)
        for item in conflicts:
          (aid, aevent, aservice_id, astart_tm_utc, aduration_tm_utc, aname_id, asname_id, alname_id, arecording) = item
          if aname_id == name_id: continue
          conflictInfo = conflictInfo + self.db.ServiceName(aservice_id) + " \"" + self.db.Sname(aname_id) + "\"<BR>\n"

        conflictInfo = conflictInfo + "</BLOCKQUOTE>\n"
    return (conflictMark, conflictInfo)


  def epgid2url(self, epg_id):
     return "id%s.html" %epg_id

  def event2html(self, epg_id):
    program = ""
    event = self.db.Epg(epg_id)
    (id, event, service_id, start_tm_utc, duration_tm_utc, name_id, sname_id, lname_id, recording) = event

    service = self.db.ServiceName(service_id)
    sname = self.db.Sname(sname_id)
    lname = self.db.Lname(lname_id)
    name = self.db.Name(name_id)

    start_tm = start_tm_utc - time.timezone
    start_local = time.localtime(start_tm_utc)
    start = time.strftime("%Y-%m-%d %H:%M:%S", start_local)

    duration_tm = duration_tm_utc
    duration_local = time.gmtime(duration_tm)
    duration = time.strftime("%H:%M:%S", duration_local)

    (g1,g2,g3, g4,g5,g6, g7,g8,g9) = duration_local
    duration_sec = g4*3600 + g5*60 + g6

    #search for conflicts
    (conflictMark, conflictInfo) = self.conflicts(start_tm_utc, duration_tm_utc, recording, name_id)

    #generate program tag
    state = ""
    if recording >= 1:
      state = "checked"
      program += "<input type=\"hidden\" name=\"epgpreset\" value=\"%d\" />\n" %(epg_id)
    program += "<input type=\"checkbox\" %s name=\"epgset\" value=\"%d\"/>" %(state, epg_id)
    program += "%s %s %s&nbsp"%(conflictMark, start, duration)

    #details start
    if len(lname) > 0 or len(sname) > 0:
      program += "<A HREF='javascript:show(%s);' title='%s'>%s</A>" %(epg_id, name, name)
      program += "&nbsp[%s]\n" %(service)
      program += "<DIV STYLE='display: none;' ID='%s' CLASS=''>"%epg_id + sname + lname + "</DIV>" + "\n"
    else:
      program += "%s&nbsp[%s]\n" %(name, service)

    # add conflict info when recording
    if recording >= 1:
      program += conflictInfo + "\n"

    return program


  def do_GET(self, urls):
    searchForm = "<P><CENTER><FORM ACTION=\"%s\" METHOD=\"POST\">\n" %(urls[0]+urls[1])
    searchForm += "<BR><INPUT TYPE=\"TEXT\" NAME=\"find\"/>"
    searchForm += "</SELECT><INPUT TYPE=\"SUBMIT\" VALUE=\"Search\"></FORM></CENTER></P>"

    return self.Body(urls[0]+urls[1], searchForm + "Welcome!")

  def do_POST(self, urls, form):
    text = ""
    self.urls = urls
    findName = "" # search text
    setrec = []
    rmrec = []

    for field in form.keys():
      field_item = form[field]
      data = []
      if type(field_item) == type([]): data = field_item
      else: data.append(field_item)

      # parse post data
      (_findName, _setrec, _rmrec) = self.parsePost(data, setrec, rmrec)
      if len(findName) == 0: findName = _findName

    #execute changes
    for epg_id in setrec:
      print "update set:", epg_id
      self.db.UpdateEpgRecording(epg_id, 1)
    for epg_id in rmrec:
      print "update reset:", epg_id
      self.db.UpdateEpgRecording(epg_id, 0)

    #reload recording
    if len(rmrec)>0 or len(setrec)>0:
      print "reload recording..."
      cmd = "kill -10 $(/root/scripts/epg/epgRecPID.sh)"
      system(cmd)

    # search
    if len(findName) == 0:
      text = "No text to search.<BR>\n"
    else:
      text = "Searching \"%s\"<BR><BR>\n" %findName

      events = self.db.Like(findName)

      if len(events) == 0:
        return "No events found."
      else:
        sout = "Found %d events."%len(events)
        url = "%s%s"%(urls[0], urls[1])
        text += "<FORM ACTION=\"%s\" METHOD=POST>\n" %url

        for event in events:
          text += self.event2html(event[0]) + "<BR>\n"

        text += "</SELECT><P><INPUT TYPE=SUBMIT VALUE=Send>"
        text += "</P><INPUT TYPE=\"HIDDEN\" NAME=\"find\" VALUE=\"%s\"></FORM>" %findName

    searchForm = "<P><CENTER><FORM ACTION=\"%s\" METHOD=\"POST\">\n" %(urls[0]+urls[1])
    searchForm += "<BR><INPUT TYPE=\"TEXT\" NAME=\"find\" VALUE=\"%s\"/>" %findName
    searchForm += "</SELECT><INPUT TYPE=\"SUBMIT\" VALUE=\"Search\"></FORM></CENTER></P>"

    return self.Body(urls[0]+urls[1], searchForm + text)


  #generate response body
  def Body(self, url, content):
    body =  "<HTML>\n"

    #rozklikavani skript
    body += "<script type=\"text/javascript\">\n  function show(id)\n  {\n"
    body += "    var a = document.getElementById(id);\n"
    body += "    a.style.display = (a.style.display == 'block')? 'none' : 'block';\n  }\n</script>\n"

    body += "<BODY>\n"
    body += content
    body += "\n</BODY></HTML>"
    return body
