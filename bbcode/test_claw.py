import time
import pwm
from claw import Claw

pwm.enable()

claw = Claw()

claw.start()

print "Close claw 25"
claw.closeClaw(25)
claw.openClaw()

print "Close claw 50"
claw.closeClaw(50)
claw.openClaw()

print "Close claw 75"
claw.closeClaw(75)
claw.openClaw()

print "Gradual close"
print "0.02 delay"
claw.closeClawGradual(90, 0.02)
claw.openClaw()

print "0.05 delay"
claw.closeClawGradual(90, 0.05)
claw.openClaw()

claw.stop()



