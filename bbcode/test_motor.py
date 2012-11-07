import pwm
from motor import Motor

pwm.enable()

motor = Motor()

#          pwmLeft, pwmRight, gpioLF, gpioLB, gpioRF, gpioRB
motor.attach("P9_16", "P9_31", "48", "49", "117", "115")
print "Attach successful!"

# move forward for 3 seconds
motor.move(3, "forward")
print "Move forward 3 seconds successful!"

# move left for 3 seconds
motor.direction(3, "left")
print "Move left 3 seconds successful!"

# move right for 3 seconds
motor.direction(3, "right")
print "Move right 3 seconds successful!"

# move back for 3 seconds
motor.move(3, "backward")
print "Move backward 3 seconds successful!"

motor.detach()
