from umb.UmbPlugin import *
import telnetlib
import time

HOST = "192.168.25.200"
PORT = 2701
BUZZER = "io set ddr 0 ff 10"
BUZZER_OFF = "io set ddr 0 00 10"

class Buzzerbouncer(UmbPlugin):
    def __init__(self):
        UmbPlugin.__init__(self)
        
    @trigger
    def openDoor(self):   
        tn = telnetlib.Telnet(HOST, PORT)
        tn.write(BUZZER+"\n")
        time.sleep(1)
        tn.write(BUZZER_OFF+"\n")
        tn.close()
