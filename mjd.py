#!/usr/bin/python
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

#Modified Julian Data conversion
# ETSI EN 300 468 - ANNEX C

def mjd2time(mjd):
  k=0
  y =  int((mjd  - 15078.2) / 365.25)
  m =  int((mjd - 14956.1 - int(y * 365.25)) / 30.6001)
  d =  mjd - 14956 - int(y * 365.25) - int(m * 30.6001)
  if (m == 14 or m == 15): k = 1
  y = y + k + 1900
  m = m - 1 - k*12

  if (y < 2000) or (y > 2050): y=2000
  if (m < 1) or (m > 12): m=1
  if (d < 1) or (d > 31): d=1

  return (y, m, d)

if __name__ == "__main__":
  print mjd2time(0xCEE8)
  print mjd2time(0xD6F5)
