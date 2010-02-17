# epg search
import os
import epgSearch

class epgWebSearch:
  def __init__(self):
    return

  # parse post parameters
  def parsePost(self, data):
    findName = ""
    setrec = []
    rmrec = []

    for mini in data:
      print "name:%s value:%s"%(mini.name, mini.value)

      service=""
      start=0
      if mini.name == "find":
        findName = mini.value

      elif mini.name == "epgset":
        delim = mini.value.find(".")
        service = mini.value[0 : delim]
        start = mini.value[delim+1 : len(mini.value)]

        #pokud je v rmrec, tak ji pouze vyjmi
        found = False
        for pos in range(len(rmrec)):
          if start == rmrec[pos]:
            found = True
            rmrec.remove(start)
            break
        if found == False:
          #pridej do setrec pokud neni v rmrec (= byla uvedena jako epgpreset ale nebyla jeste nalezena epgset)
          for pos in range(len(setrec)):
            if start == setrec[pos]:
              found = True
              break
          if found == False:
            setrec.append(start)

      elif mini.name == "epgpreset":
        delim = mini.value.find(".")
        service = mini.value[0 : delim]
        start = mini.value[delim+1 : len(mini.value)]

        #pokud je v setrec, tak ji pouze vyjmi
        found = False
        for pos in range(len(setrec)):
          if start == setrec[pos]:
            found = True
            setrec.remove(start)
            break
        if found == False:
          #pridej do rmrec pokud neni v setrec (pokud je v set nic se nemeni, pokud neni mozna jeste set nebylo nalezeno)
          for pos in range(len(rmrec)):
            if start == rmrec[pos]:
              found = True
              break
          if found == False:
            rmrec.append(start)

    return (findName, setrec, rmrec)


  def do_GET(self, urls):
    return self.Body(urls[0]+urls[1], "Welcome!")

  def do_POST(self, urls, form):
    findName = "" # search text
    text = "" # page text

    for field in form.keys():
      field_item = form[field]
      data = []
      if type(field_item) == type([]): data = field_item
      else: data.append(field_item)

      # parse post data
      (findName, rmrec, setrec) = self.parsePost(data)

      #execute changes
      for epg_id in setrec:
        self.db.UpdateEpgRecording(epg_id, 1)
      for epg_id in rmrec:
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
        searchRes = epgSearch.find(findName)
        text = text + "<BR>\n".join(searchRes.split("\n"))

    return self.Body(urls[0]+urls[1], text)


  #generate response body
  def Body(self, url, content):
    body =  "<HTML><BODY>"
    body += "<P><CENTER><FORM ACTION=\"%s\" METHOD=\"POST\">\n" % url
    body += "<INPUT TYPE=\"TEXT\" NAME=\"find\">"
    body += "</SELECT><INPUT TYPE=\"SUBMIT\" VALUE=\"Search\"></FORM></CENTER></P>"
    body += content
    body += "</BODY></HTML>"
    return body
