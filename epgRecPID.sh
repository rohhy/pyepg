#!/bin/bash
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

ps aux | grep python | grep epgRec | tr -s " " | cut -d " " -f2
