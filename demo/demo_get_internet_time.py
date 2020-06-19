#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      OVK
#
# Created:     19.05.2020
# Copyright:   (c) OVK 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import urllib.request
from datetime import datetime
import win32api

def getOnlineUTCTime():
    with urllib.request.urlopen('http://just-the-time.appspot.com/') as response:
        internettime = response.read().decode("utf-8")
    #print(type(internettime), internettime)
    OnlineUTCTime   = datetime.strptime(internettime.strip(), '%Y-%m-%d %H:%M:%S')
    #print(type(OnlineUTCTime), OnlineUTCTime)
    #datetime_object = datetime.strptime(OnlineUTCTime, '%b %d %Y %I:%M%p')

    return OnlineUTCTime

def main():
    print(datetime.now())
    OnlineUTCTime = getOnlineUTCTime()
    print(OnlineUTCTime)
    win32api.SetSystemTime( OnlineUTCTime.year,
                            OnlineUTCTime.month,
                            OnlineUTCTime.weekday(),
                            OnlineUTCTime.day,
                            OnlineUTCTime.hour-1,
                            OnlineUTCTime.minute,
                            OnlineUTCTime.second, 0)
    print(datetime.now())

    #print(datetime.utcnow() - getOnlineUTCTime())

if __name__ == '__main__':
    main()
