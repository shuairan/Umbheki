from umb.UmbPlugin import *
import time
import threading


class Test(UmbPlugin):
    #event list:
    events = ["everyTenSeconds", "testEvent"]
  
    def __init__(self):
        UmbPlugin.__init__(self, Test.events)
        self.thread_killed = False
        self.th = threading.Thread(target = self.thread)
        #self.th.start()
        
    def thread(self):
        while not self.thread_killed:
            
            self.event.everyTenSeconds()
            for i in range(10):
                time.sleep(1)
                if self.thread_killed:
                    return
    
    @trigger
    def out(self, *args):
        if len(args):
            print "Out: %s " % args
        else: 
            print "Out (empty)"
        self.raiseEvent("Test.testEvent")
        self.raiseEvent.everyTenSeconds()

    def aFoobarEvent(self, *args):
        self.raiseEvent()
