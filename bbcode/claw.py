import time
import pwm
import time
from servo import Servo 

class Claw:
	def start(self):
		pwm.enable()
		self.__servo = Servo()	
		self.__servo.attach("P9_14")
		self.__servo.writeMicroseconds(500)
		time.sleep(1)

	def openClaw(self):
		self.__servo.writeMicroseconds(500)
		time.sleep(1)
		
	def closeClaw(self, value):
		self.__servo.write(value)
		time.sleep(1)

	def closeClawGradual(self, value, delay):
		i = 0
		while i <= value:
			self.__servo.write(i)	
			time.sleep(delay)
			i = i + 1
			
	def stop(self):
		self.__servo.detach()

