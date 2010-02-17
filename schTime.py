import time

def UTCTimeToString(tm):   # sec in UTC
  return _TimeToString(time.localtime(tm))

def RAWTimeToString(tm):   # raw sec.
  return _TimeToString(time.gmtime(tm))

def _TimeToString(gtm):
  if gtm[0] < 2009:
    return time.strftime("%H:%M:%S", gtm)
  return time.strftime("%d.%m.%Y %H:%M:%S", gtm)
