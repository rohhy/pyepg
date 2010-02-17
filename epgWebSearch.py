# epg search
import os
import epgSearch

class epgWebSearch:
  def __init__(self):
    return

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
      for mini in data:
        if mini.name == "find":
          findName = mini.value
      if len(findName) == 0: return

      # search
      text = epgSearch.find(findName)
      text = "<BR>\n".join(text.split("\n"))

    return self.Body(urls[0]+urls[1], text)


  #generate response body
  def Body(self, url, content):
    body =  "<HTML><BODY>"
    body += "<FORM ACTION=\"%s\" METHOD=\"POST\">\n" % url
    body += "<INPUT TYPE=\"TEXT\" NAME=\"find\">"
    body += "</SELECT><INPUT TYPE=\"SUBMIT\" VALUE=\"Search\"></FORM>"
    body += content
    body += "</BODY></HTML>"
    return body
