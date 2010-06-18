
import socket

#Simply change the host and port values
host = '127.0.0.1'
port = 80

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	s.connect((host, port))
	s.shutdown(2)
	print "Success connecting to "
	print host + " on port: " + str(port)
except Exception, e:
	print "Cannot connect to "
	print host + " on port: " + str(port)
	print e
