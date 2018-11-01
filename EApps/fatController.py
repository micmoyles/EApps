#!/usr/bin/python
from EApp import *

class regapp():
    def __init__(self):
        name = self.name
        ts = self.timestamp

class fatController(EApp):
    
    def __init__(self):
        self.name = 'fatController'
        EApp.__init__(self,self.name) 
        self.isRegistered = True # fatController always considered registered with itself
        
        self.name_list = [] # used to keep track of what apps are registered.
	    self.app_instances = []
	    self.app_group = []
        # this should be a class where each object has a name and a timestamp of last communication
        # the fatController should continously check timestamps and ping other apps to make sure they're running
        # when an app is shutdown it should sent a deregistration message to the fatController
    
        # if the fatController recieves a registration message from an app he already knows about he shoud
        # send a kill signal to that app
    def generateResponse(self,toApp):
        return 'HEL|' +  str(toApp) + '|fatController|' + str(dt.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')) + '|'
    def generateRegistration(self,toApp):
        return 'REG|' +  str(toApp) + '|fatController|' + str(dt.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')) + '|'

    def killApp(self, toApp, ts):
       # used if a dupe app tries to register
        msg = 'KAP|' +  str(toApp) + '|fatController|' + str(ts) + '|'
        mcastSend(msg)

# Registration is done using name and the launchtime.
# if an app tries to launch we need to check that it is not registered
# if it is registered we need to send a kill app message that only the new one will respond to
# hence the distinction by timestamp

    def isDupe(self, appName, ts):
	if appName not in self.app_group: return False
        if name in name_list:
	    registered_timestamp = [x.ts for x in app_instances if x.name == name]
            registered_timestamp = registered_timestamp[0]
	    if registered_timestamp != ts: return True
	    else: return False
	
        return ts == [i.ts for i in self.app_instances if i.name == appName] 
       
    
    def mainLoop(self):
	    count = 0
	    # always send list of registered apps
        messageList = []
        msg = 'RRG|ALL|fatController|%s|%s' % (str(dt.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')),str(self.name_list))
        mcastSend( msg )
	# start listening
        while True:
          #self.log('Binding to %s:%d' % (MCAST_FC_LISTEN, MCAST_FC_LISTEN_PORT) )
          pac = sock.recv(10240)
          self.log('recv message %s is good....%s' % (pac, str(self.msgIsValid(pac))))
          if self.msgIsValid(pac):
             msgType, toApp, fromApp, ts,content = self.parseMessage(pac)
             if msgType == 'QRG':
               self.log('Recieved Registration Query....responding with %s' % str(self.name_list) )
               msg = 'RRG|ALL|fatController|%s|%s' % (str(dt.datetime.now().strftime('%Y-%m-%d-%H:%M:%S')),str(self.name_list))
               messageList.append(msg)
               #mcastSend(msg)
             elif msgType == 'HEL':
               self.log('Received greeting from %s' % fromApp)
               self.log('Politely returning greeting')
               self.name_list.append(fromApp)
               self.log(self.generateRegistration(fromApp))
               self.log(self.name_list)
          if len( messageList ) == 0:
               self.log('No messages to send')
          for msg in messageList: 
               self.log(' Sending %s ' % str(msg) )
               mcastSend(msg)   
          sleep(5)
