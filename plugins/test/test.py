from umb.UmbPlugin import *
import time
import threading


class Test(UmbPlugin):
    #event list:
    events = ["everyMinute", "testEvent"]
    event_args = {"everyMinute": ["count"],
                  "testEvent": ["bla"]}
    
    def __init__(self):
        UmbPlugin.__init__(self)
        self.thread_killed = False
        self.th = threading.Thread(target = self.thread)
        self.th.start()
        
    def thread(self):
        count = 0
        while not self.thread_killed:
            count = count+1
            self.raiseEvent.everyMinute(count)
            for i in range(60):
                time.sleep(1)
                if self.thread_killed:
                    return
    
    @trigger
    def out(self, *args):
        if len(args):
            print "Out: %s " % args
        else: 
            print "Out (empty)"
        self.raiseEvent("Test.testEvent", "argument")

    def aFoobarEvent(self, *args):
        self.raiseEvent()

    @trigger
    def deactivate(self):
        IPlugin.deactivate(self)
        self.thread_killed = True
