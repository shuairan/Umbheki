from umb.UmbPlugin import *
import xml.dom.minidom
import urllib
import time
import threading

VLC_WEB_STATUS_URL = "http://localhost:8080/requests/status.xml"
VLC_PLAY = "?command=pl_play"
VLC_PAUSE = "?command=pl_pause"
VLC_STOP = "?command=pl_stop"
PLAYING = "playing"
STOPPED = "stop"
PAUSED = "paused"

class VLC(UmbPlugin):
    #event list:
    events = ["stopped"]
    
    def __init__(self):
        UmbPlugin.__init__(self, VLC.events)
        self.lastState = None
        
        self.thread_killed = False
        self.th = threading.Thread( target = self.thread)
        self.th.start()
        
    def thread(self):
        while not self.thread_killed:
            self.checkState()
            for i in range(5):
                time.sleep(1)
                if self.thread_killed:
                    return
        
    @event
    def stopped(self, *args):
        self.raiseEvent()
    
    @trigger
    def play(self):
        state = self.getVlcState()
        if state==PLAYING or state==PAUSED:
            urllib.urlopen(VLC_WEB_STATUS_URL+VLC_PLAY)

    @trigger
    def pause(self):
        state = self.getVlcState()
        if state==PLAYING:
            urllib.urlopen(VLC_WEB_STATUS_URL+VLC_PAUSE)

    @trigger 
    def stop(self):
        state = self.getVlcState()
        if state==PLAYING or state==PAUSED:
            urllib.urlopen(VLC_WEB_STATUS_URL+VLC_STOP)

    def checkState(self):
        state = self.getVlcState()
        if state==STOPPED and self.lastState==PLAYING:
            self.stopped()
        self.lastState = state

    def getVlcState(self, url=VLC_WEB_STATUS_URL):
        vlcxml = xml.dom.minidom.parse(urllib.urlopen(url))
        curstate = vlcxml.getElementsByTagName('state')[0].firstChild.toxml()
        return curstate
