import datetime
import pwm
import os
import signal
import sys
import select
from proximity import Proximity

pwm.enable()

__prox = Proximity()

__prox.attach("P9_16", "48")

__prox.start()

#fd = os.open("/sys/class/gpio/gpio48/value", os.O_RDONLY | os.O_NONBLOCK)

#READ_ONLY = select.POLLPRI
#poller = select.poll()
#poller.register(fd, READ_ONLY)


#def signal_handler(signal, frame):
#	print 'cleaning up'
#	__prox.detach()
#	open("/sys/class/gpio/unexport", 'w').write("48")
#	fd.close()
#	sys.exit(0)

#toggle = 0
#pre = 0
#post = 0
#while True:
#	events = poller.poll(-1)
#	
#        os.lseek(fd, 0, 0)
#	
#	if((toggle == 0) and (os.read(fd, 2) == '1\n')):
#		toggle = 1	
#		#open("/sys/class/gpio/gpio48/edge", 'w').write("falling")
#		pre = datetime.datetime.now().microsecond
#
#	if((toggle == 1) and (os.read(fd, 2) == '0\n')):
#		toggle = 0
#		#open("/sys/class/gpio/gpio48/edge", 'w').write("rising")
#		post = datetime.datetime.now().microsecond
#		print "Delta: ", (post - pre)
#		
#signal.pause()
