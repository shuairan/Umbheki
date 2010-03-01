from umb.UmbPlugin import *
import os

ON = 1
OFF = 0

class Monitor(UmbPlugin):
    def __init__(self):
        UmbPlugin.__init__(self)
        self.status = ON
        
    @trigger
    def standby(self):
        output = os.popen("xset -display :0.0 dpms force standby").read()
        logger.debug("monitor standby; %s" % output)
        return output
        
    @trigger
    def on(self):
        output = os.popen("xset -display :0.0 dpms force on").read()
        self.logger.debug("monitor on; %s" % output)
        return output
    
    @trigger
    def test(self, *args):
        self.callTrigger("Test.out", *args)
