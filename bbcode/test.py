import os
import enc
import claw
import proximity
import pwm

pwm.enable()
os.system('./map')

enc.pollEnc
claw.claw_open()

os.system('./map')
enc.pollEnc()
enc.pollEnc()
claw.claw_close()

os.system('./map')
enc.pollEnc()
enc.pollEnc()

prox = proximity.Proximity()
prox.attach("51", "P9_42", "48")
pipein = prox.start()

count = 0
while count < 32:
	val = os.read(pipein,64)
	print 'Distance' + str(val)
	encvals = enc.pollEnc()
	print encvals
	count = count+1

prox.stop()

while(1):
	enc.pollEnc()
