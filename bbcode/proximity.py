import pwm
import select
import datetime
import time
import signal
import os

from pinout import *
from claw import Claw

# Proximity specific PWM configuration
PRX_DUTY_NS = 500000
PRX_PWM_FREQ = 3 #hz

SRV_MIN_DUTY_NS = 200000
SRV_MAX_DUTY_NS = 2000000
SRV_PWM_FREQ = 50 #hz
SRV_DEGREE_TO_NS = (SRV_MAX_DUTY_NS - SRV_MIN_DUTY_NS)/180

class Proximity:
	def attach(self, gpio_trig, pwm_pin_serv, gpio):
		if (not pwm_pin_serv in pwm_pins):
			raise Exception('Pin ' + pwm_pin_prox + ' and/or ' + pwm_pin_serv + ' is not pwm capable')
		else:
			self.__pwm_pin_serv = PWM_PATH+pwm_pins[pwm_pin_serv]["pwm"]	
			self.__pwm_serv_request = self.__pwm_pin_serv + "/request"
			self.__pwm_serv_run = self.__pwm_pin_serv + "/run"
			self.__pwm_serv_duty_ns = self.__pwm_pin_serv + "/duty_ns"
			self.__pwm_serv_period_freq = self.__pwm_pin_serv + "/period_freq"
			
			self.__gpio = GPIO_PATH+"/gpio"+gpio
			self.__gpio_num = gpio
			self.__gpio_direction = self.__gpio + "/direction";
			self.__gpio_edge = self.__gpio + "/edge";
			self.__gpio_value = self.__gpio + "/value";
			
			self.__gpio_trig = GPIO_PATH+"/gpio"+gpio_trig
			self.__gpio_trig_num = gpio_trig
			self.__gpio_trig_direction = self.__gpio_trig + "/direction";
			self.__gpio_trig_edge = self.__gpio_trig + "/edge";
			self.__gpio_trig_value = self.__gpio_trig + "/value";
		
	
			
		#	val = f_read(self.__pwm_serv_request)
		#	if val.find('free') < 0:
		#		raise Exception('Pin ' + self.__pwm_pin_serv + ' is already in use')
		
			f_write(GPIO_PATH + "/export", self.__gpio_num)
			f_write(self.__gpio_direction, "in")
			f_write(self.__gpio_edge, "falling")	
			#f_write(self.__gpio_edge, "both")	
			
			print 'Set gpio trig'	
			f_write(GPIO_PATH + "/export", self.__gpio_trig_num)
			f_write(self.__gpio_trig_direction, "out")
		        f_write(self.__gpio_trig_value, "0")
	
			print 'Done set gpio trig'	
			f_write(self.__pwm_serv_request, "1")
			f_write(self.__pwm_serv_run, "0")
			f_write(self.__pwm_serv_period_freq, str(SRV_PWM_FREQ))
			f_write(self.__pwm_serv_duty_ns, str(SRV_MIN_DUTY_NS))
			f_write(self.__pwm_serv_run, "1")

			self.__pos = 0

	def write(self, value):
		f_write(self.__pwm_serv_run, "1")
		duty_ns = SRV_MIN_DUTY_NS + value * SRV_DEGREE_TO_NS
		self.__lastValue = value
		f_write(self.__pwm_serv_duty_ns, str(duty_ns))
		time.sleep(0.5)
		f_write(self.__pwm_serv_run, "0")

	def gotoright(self):
		self.write(75)
		
	def gotocenter(self):
		self.write(125)
		
	def gotoleft(self):
		self.write(175)

	def changepos(self):
		val = ""
		if(self.__pos == 0):
			val = "rght"
			self.gotoright()
			self.__pos = self.__pos + 1
		elif(self.__pos == 1):
			val = "cntr"
			self.gotocenter()
			self.__pos = self.__pos + 1
		elif(self.__pos == 2):
			val = "left"
			self.gotoleft()
			self.__pos = self.__pos + 1
		elif(self.__pos == 3):
			val = "cntr"
			self.gotocenter()
			self.__pos = 0
		
		return val

	def start(self):
		pipein, pipeout = os.pipe()
		
		self.__pid = os.fork()
	
		if self.__pid == -1:
			raise Exception("Fork failed!")
		if self.__pid == 0:	
		        f_write(self.__gpio_trig_value,"0")
			fd = os.open(self.__gpio_value, os.O_RDONLY)
		
			READ_ONLY = select.POLLPRI
			poller = select.poll()
			poller.register(fd, READ_ONLY)
			
			pre = 0
			post = 0
			count = 0
			
			position = self.changepos()	
			
			pre = datetime.datetime.now().microsecond
		        f_write(self.__gpio_trig_value, "1")
		        time.sleep(0.000010)
			f_write(self.__gpio_trig_value, "0")
			
			while True:
				events = poller.poll(-1)	
				os.lseek(fd, 0, 0)
			
				if(os.read(fd, 2) == '0\n'):
					post = datetime.datetime.now().microsecond
					#f_write(self.__gpio_trig_value, "0")
				
					if count != 0:	
						val = "%s%d" % (position, (post - pre))
						os.write(pipeout, val)

					count = count + 1
					if count == 5:
						position = self.changepos()
						time.sleep(1.75)
						count = 0
					
					pre = datetime.datetime.now().microsecond
					f_write(self.__gpio_trig_value,"1")
		        		time.sleep(0.000010)
					f_write(self.__gpio_trig_value, "0")
					
		else:
			return pipein

	def stop(self):
		os.kill(self.__pid, signal.SIGKILL)
		 	
	def detach(self):
		#f_write(self.__pwm_prox_run, "0")
		#f_write(self.__pwm_prox_request, "0")
			
		f_write(self.__pwm_serv_run, "0")
		f_write(self.__pwm_serv_request, "0")
			
		f_write(GPIO_PATH + "/unexport", self.__gpio_num)

	def __del__(self):
		self.detach()

# prox test
#pwm.enable()
#prox = Proximity()

#prox.attach("P9_16", "P9_29", "48")
#pipein = prox.start()

#count = 0
#while count < 40:
#	val = os.read(pipein, 64)
#	print '1: count = %d\nval = %s\n' % (count, val)
#	count = count + 1

#prox.stop()
#prox.detach()

#claw_servo = Claw()

#claw_servo.attach("P9_14")
#claw_servo.openClaw()
#claw_servo.closeClaw(200)
#claw_servo.openClaw()
#claw_servo.closeClaw(100)
#claw_servo.openClaw()
#claw_servo.detach()

#prox.attach("P9_16", "P9_29", "48")
#pipein = prox.start()

#count = 0
#while count < 40:
#	val = os.read(pipein, 64)
#	print '2: count = %d\nval = %s\n' % (count, val)
#	count = count + 1

#prox.stop()
#prox.detach()

#print "done killin!"
#while 1:
#	prox.gotoright()
#	prox.gotoleft()

#while 1:
#	prox.changepos()
