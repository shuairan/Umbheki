from umb.UmbPlugin import *
import time
import threading
from telnetlib import Telnet
import re
import os
import string

IP = "192.168.25.1"
PORT = 1012
PASSWORD = "fr1tzb0x"
MSN = "*"
CITY_PREFIX = "0721"


class Fritzbox(UmbPlugin):
    #event list:
    events = [ "incomingCall" ]
    event_args = {"incomingCall": ["phonenumber", "alias", "msn"] }
    
    def __init__(self):
        UmbPlugin.__init__(self)
        self.mythread = ListenThread(self)
        self.mythread.setDaemon(True)
        self.mythread.start()
        
    def thread(self):
        while not self.thread_killed:
            self.checkFritzbox()
            time.sleep(1)
            if self.thread_killed:
                return
    
    @trigger
    def call(self, *args):
        logger.debug("Calling a Trigger that is not yet implemented")
        


class ListenThread( threading.Thread ):
    """ 
    This class is the heart of the programm. It takes care of polling the Fritzbox
    and listening for calls being signalled.
    """ 
    
    def __init__(self, parent, debugIt=False):
        """ 
        This function initializes pynotify and staring the polling thread.
        """ 
        self.parent = parent
        self.logger = parent.logger
        self.debugIt = debugIt
        
        self.logger.debug("Fritzbox Listener started")

        # start polling
        self.telnet = Telnet()
        self.cancel_event = threading.Event()
        self.counter = 10
        self.running = False
        self.data_array = []
        
        threading.Thread.__init__(self)
    
    def run(self):
        """ 
        This function polls the Fritzbox and listens for calls being signalled.
        """ 
        
        while not self.cancel_event.isSet( ):
            if (self.debugIt): self.self.logger.debug("starting thread activities")

            if self.counter == 15:

                if (self.debugIt): self.logger.debug("testing connection")
                self.ping_ok = self.is_ping_ok_( )
                self.counter = 0

                # if connection present
                if self.ping_ok:
                    if (self.debugIt): self.logger.debug("connection present")
                    # if not running yet
                    if self.running == False:
                        self.logger.debug("connecting")

                        # try to connect to the Fritzbox
                        try:
                            self.telnet.open( IP, int(PORT) )
                            self.running = True

                            self.logger.debug("Connected to Fritz!Box")

                        except socket.error:
                            self.running = False
                            self.logger.error("ERROR: please check if you enabled the interior callerid of the\n\tFritzbox by calling #96*5* on your phone once and\n\tthat you are listening on the correct port")
                        except:
                            self.running = False
                            self.logger.error("ERROR: ", sys.exc_info( )[0])
                        
                # if no connection
                else:
                    self.logger.debug("no connection")
                    if self.running == True:
                        self.logger.debug("closing connection")
                        try:
                            self.telnet.close( )
                            self.running = False
                        except:
                            self.running = False
                            self.logger.error("ERROR: ", sys.exc_info( )[0])

                        self.logger.debug("Connection lost")

            self.counter = self.counter + 1
            
            if self.running == True:

                # poll the Fritzbox for new events
                if (self.debugIt): self.logger.debug("connected and reading data")
                try:
                    self.incomming_data = self.telnet.read_very_eager( )
                    self.data_array = string.split( self.incomming_data, ";" )
                except:
                    self.logger.error(sys.exc_info()[1])
 
                # if the returned data_array is filled with results, get active!
                if ( len( self.data_array ) >= 5 ):


                    # in case of an incomming call signal (RING)
                    if ( self.data_array[1] == "RING" ):

                        # check MSN
                        self.ignore = False
                        self.msn = self.data_array[4]
                        if (MSN=="*" or MSN.find(self.msn) >= 0):
                            self.logger.info("number %s reports some activity" % (self.msn))
                        else:
                            self.logger.info("number %s reports some activity - and will be ignored" % (self.msn))
                            self.ignore = True

                        if (not(self.ignore)):

                            self.logger.info("incoming phone call ..RING..RING..")
                            
                            
                            # if a telephone number is received with the call
                            if ( self.data_array[3] != "" ):

                                # search for alias name of person calling
                                self.logger.debug("searching for alias name of person calling")
                                self.phonenumber = self.data_array[3]
                                self.alias = get_name_( self.phonenumber, True )

                                self.logger.info('incoming phonecall from %s' % (self.alias))

                            # if no telephone number is received with the call
                            else:
                                self.logger.info("phonecall from an unknown person")
                                self.phonenumber = 'unknown'
                                self.alias = 'unknown'
                            
                            self.parent.raiseEvent("Fritzbox.incomingCall", self.phonenumber, self.alias, self.msn)
                            
                            # display popup message
                            #self.emit_notification_(_('incoming phonecall'), self.phonenumber, self.alias, self.msn)
                        
                            # save phonecall as unanswered in the call history
                            #calldate,calltime = self.data_array[0].strip( ).split( " " )
                            #self.save_calls_( "Callinfailed", calldate, calltime, self.phonenumber )
                        
                    # in case of an answered phonecall (CONNECT)
                    elif ( self.data_array[1] == "CONNECT" ):

                        # check MSN
                        self.ignore = False
                        self.msn = self.data_array[4]
                        if ((MSN == "*") or (MSN.find(self.msn) >= 0)):
                            self.logger.info("number %s reports some activity" % (self.msn))
                        else:
                            self.logger.info("number %s reports some activity - and will be ignored" % (self.msn))
                            self.ignore = True

                        if (not(self.ignore)):

                            self.logger.info("answered phonecall")

                    # in case of an outgoing phonecall (CALL)
                    elif ( self.data_array[1] == "CALL" ):

                        # check MSN
                        self.ignore = False
                        self.msn = self.data_array[4]
                        if ((MSN == "*") or (MSN.find(self.msn) >= 0)):
                            self.logger.info("number %s reports some activity" % (self.msn))
                        else:
                            self.logger.info("Inumber %s reports some activity - and will be ignored" % (self.msn))
                            self.ignore = True


                        if (not(self.ignore)):

                            self.logger.info("outgoing phonecall")

                            # if the called number does not start with a 0, add the city prefix
                            # to the number, to allow reverse lookup and unitary entries in the telephone book
                            if self.data_array[5][0] != '0':
                                self.phonenumber = CITY_PREFIX + self.data_array[5]
                            else:
                                self.phonenumber = self.data_array[5]

                            # search for alias name of person called
                            self.logger.debug("searching for alias name of person called")
                            self.alias = get_name_( self.phonenumber, True, "notification", self )

                            self.logger.info('outgoing phonecall to %s' % (self.alias))
                
                    # otherwise the signal means that a phonecall ended.
                    # else:
                    #    print _('INFO: phonecall terminated')

            time.sleep(1)


        # closing thread
        self.logger.debug("closing thread")
        self.telnet.close( )

        return

    
    def is_ping_ok_( self ):
        """ 
        This function checks the ping to the Fritzbox
        """

        # try to ping the Fritzbox
        if (self.debugIt): self.logger.debug('pinging the Fritzbox')
        self.lifeline = re.compile( r"(\d) received" )
        self.report = ( "0","1","2" )
        self.result = 0
        self.pingaling = os.popen( "ping -q -c2 -w2 "+IP,"r" )
        sys.stdout.flush( )

        while 1:
            self.line = self.pingaling.readline( )
            if not self.line: break
            self.igot = re.findall( self.lifeline,self.line )

            if self.igot:
                self.result = int( self.report[int( self.igot[0] )] )

        # ping failed        
        if self.result == 0:
            return False
        
        # ping successful
        else:
            return True


def get_name_(number, withinvers, subjecttype="none", subject="none"):
    return number
