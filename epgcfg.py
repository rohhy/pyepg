#!/usr/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

import ConfigParser

class epgConf:
  def __init__(self):
    self.fileConf = "epg.conf"
    default = {"count":"1","RecPath":"/tmp", "ArchPath":"~"}
    self.conf = ConfigParser.SafeConfigParser(default)
    self.conf.ReadConf()


  def ReadConf():
    with open(self.fileConf, 'rb') as configfile:
      config.read(self.configfile)
      
      self.cardsCount = self.conf.getint('DVBCard', 'count')
      self.pathRec = self.conf.get('Paths', 'RecPath')
      self.pathAchive = self.conf.get('Paths', 'ArchPath')
