#!/usr/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

class EventStack:
  def __init__(self):
    self.stack = []

  def Clear(self):
    del self.stack

  def Add(self, element):
    idx = 0
    for item in self.stack:
      if element.tmStart > item.tmStart:
        break
      idx = idx + 1

    if idx < len(self.stack):
      self.stack.insert(idx, element)
    else:
      self.stack.append(element)

  def Del(self, element):
    self.stack.remove(element)

  def ToString(self):
    if len(self.stack) == 0: return "empty"
    pos=0;
    msg="";
    for elm in self.stack:
      msg = msg + "  %d: %s\n"%(pos, elm.ToString())
      pos = pos + 1
    return msg[0 : len(msg)-1]
