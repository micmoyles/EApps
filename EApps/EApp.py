#!/usr/bin/python
import socket
from time import sleep
import datetime as dt
import struct
import sys


MCAST_FC_LISTEN = '224.1.1.1'
MCAST_FC_LISTEN_PORT = 5007

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((MCAST_FC_LISTEN, MCAST_FC_LISTEN_PORT))  # use MCAST_FC_LISTEN instead of '' to listen only
                             # to MCAST_FC_LISTEN, not all groups on MCAST_FC_LISTEN_PORT
mreq = struct.pack("4sl", socket.inet_aton(MCAST_FC_LISTEN), socket.INADDR_ANY)

sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

def mcastSend(data):
    #MCAST_FC_LISTEN, MCAST_FC_LISTEN_PORT = dest ,port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL,20)
    sock.sendto(data,(MCAST_FC_LISTEN, MCAST_FC_LISTEN_PORT))
    
from_FC = ['HEL','REG','RRG','TRD','KAA','KAP']
to_FC   = ['REG','HEL','QRG']
# KAA = Kill All Apps
# KAP - kill just one app
# QRG - Query Registration, the fc will return a list of all apps registered, which should include itself. This should prevent a second instance of the fc from launching
# RRG - response message from FC


class EApp:
    def __init__(self, name):
        self.name = name
        self.inCharge = True if self.name == 'fatController' else False
        self.isRegistered = False
        self.log('Starting... %s is in charge....%s' % (self.name,str(self.inCharge)))
	self.launchtime = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.lastRegistrationRecvd = None
        
    def log(self,text):
        #logfile = '%s-log-%s' % (self.name, dt.datetime.now().strftime('%Y%m%d') )
        logfile = 'log-%s' % (dt.datetime.now().strftime('%Y%m%d') )
        f = open(logfile,'a')
        logtext = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' ' + str(self.name) + ' ' + str(text) + '\n'   
        f.write(logtext)
        f.close()
        
    def queryRegistrations(self):
        self.log('querying registrations')
        msg = 'QRG|fatController|%s|%s|' % (self.name, dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        mcastSend(msg)
        
    def generateHello(self):
        if not self.inCharge:
            return 'HEL|fatController|' +  str(self.name) + '|' + str(self.launchtime) + '|'
        else:
            sys.exit('Tried to register myself...:(')
            
    def parseMessage(self,msg):
        msgType, toApp, fromApp, ts,content = msg.split('|')
        return msgType, toApp, fromApp, ts, content
    
    def msgIsValid(self,msg):
        
    # message must have format
    # messageType(3chars)|toApp(string)|fromApp(string)|launch_timestamp(YYYYMMDD-HH:MM:SS)    
    
       if msg.count('|') < 3:
        return False
       self.log(msg)
       msgType, toApp, fromApp, ts, content = msg.split('|') 
       if not self.inCharge and msgType not in from_FC:
           self.log('Dropping message: not valid from FC %s' % msgType)
           return False
       elif self.inCharge and msgType not in to_FC: 
           self.log('Dropping message: not known to FC  %s' % msgType)
           return False
       elif msgType == 'KAA': 
	   self.log('Exiting due to received KAA message')
	   sys.exit()
       elif toApp not in [self.name,'ALL']:
           self.log('Dropping message: %s for %s instead' % (msg,toApp))
           return False
       else:
           return True

class talker(EApp):
    def __init__(self, name):
        EApp.__init__(self,name)      
        self.register()
    def register(self):
        count = 0 # if this reaches 5 without a registration response then exit
#        message = self.generateHello()
#        self.log('Sending greeting %s - %s' % (self.generateHello(), str(count)))
#        mcastSend(message)

# First step is to wait 5s for a registration message from the FC
# if self is found in the registration list then exit

        while count < 5 and not self.isRegistered:
            # this is where the app will register itself with the fatController
#            self.log('Binding to %s:%d' % (MCAST_FC_LISTEN, MCAST_FC_LISTEN_PORT) )
            msg = sock.recv(10240)
            if self.msgIsValid(msg):
               self.log('recv message %s is good....%s' % (msg, str(self.msgIsValid(msg))))
            else:
                self.log('Garbage received....%s' % msg)
            msgType, toApp, fromApp, ts, content = msg.split('|') 
            if msgType == 'RRG' and self.name in content:
               self.log('Already registered...exiting')
               sys.exit()
            if msgType == 'RRG' and self.name not in content:
               self.log('Self not found in FC register...exiting gracefully')
               sys.exit()
            elif msgType == 'RRG' and self.name in content:
                self.isRegistered = True
                self.lastRegistrationRecvd = ts
                self.log('Now registered')
            sleep(1)
            self.queryRegistrations()
            count+=1

class middleMan(talker):
# this will open a tcp socket and listen to commands from the GUI
    def __init__(self, name):
        talker.__init__(self,name)      

class msg_loader(talker):
# this will listen to all messages and load the relevant ones to the hanger 
    def __init__(self, name):
        talker.__init__(self,name)      

