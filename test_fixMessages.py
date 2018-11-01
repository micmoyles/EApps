#!/usr/bin/python

import fixMessages

m = fixMessages.MessageHandler('MIKE00','TEST00')
print m.getlogon()
print m.getHeartBeat(1,150)