#!/usr/bin/python


from daemon import Daemon
import time, sys
import os
import logging
from umb import main

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

main_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(main_dir + "/umb")

class Umbheki(Daemon):
    def foobar(self):
        print self.id()

    def run(self):
        self.umbheki = main.Umbheki()
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print 'daemon stopped by user request. shutting down.'
                break

if __name__ == "__main__":
    umbheki = Umbheki('/tmp/umbheki.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            umbheki.start
        elif 'debugstart' == sys.argv[1]:
            umbheki.debugmodus=True
            umbheki.start()
        elif 'stop' == sys.argv[1]:
            umbheki.stop()
        elif 'restart' == sys.argv[1]:
            umbheki.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|debugstart|stop|restart" % sys.argv[0]
        sys.exit(2)
