import pwm
import time

from pinout import *

# Claw specific PWM configurations
CLW_OFF_DUTY_NS = 0
CLW_MIN_DUTY_NS = 200000
CLW_MAX_DUTY_NS = 2000000
CLW_PWM_FREQ = 50 #hz
CLW_DEGREE_TO_NS = (CLW_MAX_DUTY_NS - CLW_MIN_DUTY_NS)/180

class Claw:
	def attach(self, pwm_pin):
		if not pwm_pin in pwm_pins:
			raise Exception('Pin ' + pwm_pin + ' is not pwm capable')
		else:
			self.__pwm_pin = PWM_PATH+pwm_pins[pwm_pin]["pwm"]
			
			self.__pwm_request = self.__pwm_pin + "/request"
			self.__pwm_run = self.__pwm_pin + "/run"
			self.__pwm_duty_ns = self.__pwm_pin + "/duty_ns"
			self.__pwm_period_freq = self.__pwm_pin + "/period_freq"
			

			val = f_read(self.__pwm_request)
			#if val.find('free') < 0:
			#	raise Exception('Pin ' + self.__pwm_pin + ' is already in use')

			f_write(self.__pwm_request, "1")
			f_write(self.__pwm_run, "0")
			f_write(self.__pwm_period_freq, str(CLW_PWM_FREQ))
			f_write(self.__pwm_duty_ns, str(CLW_MIN_DUTY_NS))
			f_write(self.__pwm_run, "1")

			self.__attached = True
		
	def write(self, value):
		f_write(self.__pwm_run, "1")
		duty_ns = CLW_MIN_DUTY_NS + value * CLW_DEGREE_TO_NS
		self.__lastValue = value
		f_write(self.__pwm_duty_ns, str(duty_ns))
		time.sleep(1)
		f_write(self.__pwm_run, "0")
		
	def writeMicroseconds(self, value):
		f_write(self.__pwm_run, "1")
		f_write(self.__pwm_duty_ns, str(value)+"000") #micro to nano
		time.sleep(1)
		f_write(self.__pwm_run, "0")
	
	def openClaw(self):
		self.writeMicroseconds(500)
	
	def closeClaw(self, value):
		self.write(value)
	
	def detach(self):
		f_write(self.__pwm_request, "0")
		f_write(self.__pwm_run, "0")
			
		self.__attached = False
	
	def __del__(self):
		self.detach()
	
def claw_open():
	claw_servo = Claw()
	claw_servo.attach("P9_14")
	claw_servo.openClaw()
	time.sleep(0.5)
	claw_servo.detach()
def claw_close():
	claw_servo = Claw()
	claw_servo.attach("P9_14")
	claw_servo.closeClaw(100)
	time.sleep(0.5)
	claw_servo.detach()
# claw test
#os.system('./map')
#pwm.enable()
#claw_servo = Claw()

#claw_servo.attach("P9_14")

#claw_servo.openClaw()
#claw_servo.closeClaw(100)
#claw_servo.openClaw()
#claw_servo.closeClaw(100)
#claw_servo.openClaw()	
#claw_servo.closeClaw(100)
#claw_servo.openClaw()
#claw_servo.detach()
