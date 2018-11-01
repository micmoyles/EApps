#!/usr/bin/python
import datetime
import fix_constants

class MessageHandler(object):

    def __init__(self,senderCompID,targetCompID,heartbeat = 10):
        '''
        class to handle messages generation
        :param senderCompID:
        :param targetCompID:

        Each message generator needs to
         - call getCommon()
         - append any specific tags to the message
         - call getLength()
         - add checksum and encode
        '''

        self.senderCompID = senderCompID
        self.targetCompID = targetCompID
        self.heartbeat    = heartbeat
        self.messageCommon = None

    def newHeader(self):
        return '8=FIX.4.2|9=%(len)03d|'


    def getCommon(self, messageType, sequence):

        '''
        Common components of all messages here
        messageHeader:
         - FIX type
         - message length
        messageCommon:
         - messageType (35)
         - sequenceNumber (34)
         - senderCompId (49)
         - targetCompId (56)
         - messageSendingTime (52)

         Needs to be called when each message is created to ensure the sendingTime is correct
        '''
        self.message = ''
        self.messageHeader = '8=FIX.4.2|9=%(len)03d|'

        self.messageCommon   ='35=%(type)s|34=%(seq)d|49=%(sci)s|56=%(tci)s|52=%(st)s|'
        self.messageChecksum = '10=%(checksum)03d|'

        sendingTime = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')

        self.messageCommon = self.messageCommon % \
                           {'type': messageType,
                            'seq': sequence,
                            'sci': self.senderCompID,
                            'tci': self.targetCompID,
                            'st': sendingTime
                            }



    def getlogon(self, resetSequences = True):

        '''
        :param resetSequences:
        :return: fix logon messages (encryption always set to False - 98=0)
        '''
        self.getCommon('A',1)

        if resetSequences:
            self.messageCommon += '108=%d|141=Y|98=0|' % self.heartbeat
        else:
            self.messageCommon += '108=%d|141=N|98=0|' % self.heartbeat

        return self.encodeMessage()

    def getHeartBeat(self, sequence, testReqID = None):

        self.getCommon(0,sequence)

        if testReqID:
            self.messageCommon+='112=%d|'%testReqID

        print 'Within getHeartbeat'
        print self.messageCommon

        return self.encodeMessage()


    def getTestRequest(self):
        pass

    def encodeMessage(self):

        self.messageHeader = self.messageHeader % {'len': self.getLength()}

        self.message = self.messageHeader + self.messageCommon
        '''
        calculating the checksum must be done on all tags except the content of 10
        '''
        checksum = self.getChecksum()
        self.message += self.messageChecksum % {'checksum': checksum}
        print self.message
        return self.message.replace('|',b'\x01').encode()


    def getLength(self):
        '''
        :return: length of the fix message to populate tag 9.
         Does not include tag 8, 9 or 10

         We need to ensure that getCommon() has been called to insert the appropriate content
         to the common message tags
        '''
        assert self.messageCommon is not None, 'Need to call getCommon() first'
        s = self.messageCommon
        s.replace('|',b'\x01')
        return len(s.encode())

    def getChecksum(self):

        for tag in ['8=','9=','49=','56=','52=']:
            assert tag in self.message, 'Did not find %s in %s, cannot determine checksum' % ( tag , self.message )

        sum=0
        messageString = self.message.replace('|',b'\x01')
        for c in messageString:
            sum+=ord(str(c))
        return sum % 256
