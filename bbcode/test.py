import os
import enc
import claw
import proximity
import pwm
import time

print 'PWM ENABLE/map'
pwm.enable()
os.system('./map')

enc.pollEnc()

print 'Proximity Init'

prox = proximity.Proximity()
prox.attach("38", "P9_42", "48")
pipein = prox.start()

#print 'while 1'

#prev_pos = ''
#while 1:
#	val = os.read(pipein,64)
#	pos = val[0:4]
#	dist = val[4:]
#
#	if pos != prev_pos:
#		print ''
#		print ''	
#		prev_pos = pos

	#print 'val= ' + str(val)
	#print 'pos= ' + str(pos)
#	print str(dist)
		

prox.stop()

prox.detach()

#count = 0

#while count < 10:
#	enc.startTimer()
#	time.sleep(0.05)
#	print 'Count = '
#	print str(0.05)
#	print 'Time = '
#	print enc.stopTimer()
#	print ''
#	print ''
#	count = count + 1

