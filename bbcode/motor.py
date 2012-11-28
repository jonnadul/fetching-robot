import pwm
import select
import datetime
import time
import signal
import os
import ctypes

from mmap import mmap
import struct
import enc 

from pinout import *
from claw import Claw
from proximity import Proximity

#Motor specific PWM configuration
MTR_MIN_DUTY_NS = 0
MTR_MAX_DUTY_NS = 8000000 #2 ms
MTR_PWM_FREQ = 50 #hz 
	
class Motor:
	def attach(self, pwm_pin_left, pwm_pin_right, 
                   gpio_left_front, gpio_left_back,
                   gpio_right_front, gpio_right_back):
		
		if (not pwm_pin_left in pwm_pins) or (not pwm_pin_right in pwm_pins):
			raise Exception('Pin ' + pwm_pin_left + ' and/or ' + pwm_pin_right + ' is not pwm capable')
		else:
			self.__pwm_pin_left = PWM_PATH+pwm_pins[pwm_pin_left]["pwm"]	
			self.__pwm_left_request = self.__pwm_pin_left + "/request"
			self.__pwm_left_run = self.__pwm_pin_left + "/run"
			self.__pwm_left_duty_ns = self.__pwm_pin_left + "/duty_ns"
			self.__pwm_left_period_freq = self.__pwm_pin_left + "/period_freq"
			
			self.__pwm_pin_right = PWM_PATH+pwm_pins[pwm_pin_right]["pwm"]	
			self.__pwm_right_request = self.__pwm_pin_right + "/request"
			self.__pwm_right_run = self.__pwm_pin_right + "/run"
			self.__pwm_right_duty_ns = self.__pwm_pin_right + "/duty_ns"
			self.__pwm_right_period_freq = self.__pwm_pin_right + "/period_freq"
		
			self.__gpio_left_front = GPIO_PATH+"/gpio"+gpio_left_front
			self.__gpio_left_front_num = gpio_left_front
			self.__gpio_left_front_direction = self.__gpio_left_front + "/direction";
			self.__gpio_left_front_edge = self.__gpio_left_front + "/edge";
			self.__gpio_left_front_value = self.__gpio_left_front + "/value";
			
			self.__gpio_left_back = GPIO_PATH+"/gpio"+gpio_left_back
			self.__gpio_left_back_num = gpio_left_back
			self.__gpio_left_back_direction = self.__gpio_left_back + "/direction";
			self.__gpio_left_back_edge = self.__gpio_left_back + "/edge";
			self.__gpio_left_back_value = self.__gpio_left_back + "/value";
			
			self.__gpio_right_front = GPIO_PATH+"/gpio"+gpio_right_front
			self.__gpio_right_front_num = gpio_right_front
			self.__gpio_right_front_direction = self.__gpio_right_front + "/direction";
			self.__gpio_right_front_edge = self.__gpio_right_front + "/edge";
			self.__gpio_right_front_value = self.__gpio_right_front + "/value";
			
			self.__gpio_right_back = GPIO_PATH+"/gpio"+gpio_right_back
			self.__gpio_right_back_num = gpio_right_back
			self.__gpio_right_back_direction = self.__gpio_right_back + "/direction";
			self.__gpio_right_back_edge = self.__gpio_right_back + "/edge";
			self.__gpio_right_back_value = self.__gpio_right_back + "/value";
				
			#val = f_read(self.__pwm_left_request)
			#if val.find('free') < 0:
			#	raise Exception('Pin ' + self.__pwm_pin_left + ' is already in use')
			
			#val = f_read(self.__pwm_right_request)
			#if val.find('free') < 0:
			#	raise Exception('Pin ' + self.__pwm_pin_right + ' is already in use')
			
			f_write(GPIO_PATH + "/export", self.__gpio_left_front_num)
			f_write(self.__gpio_left_front_direction, "out")
			f_write(self.__gpio_left_front_edge, "both")	
			
			f_write(GPIO_PATH + "/export", self.__gpio_left_back_num)
			f_write(self.__gpio_left_back_direction, "out")
			f_write(self.__gpio_left_back_edge, "both")	
			
			f_write(GPIO_PATH + "/export", self.__gpio_right_front_num)
			f_write(self.__gpio_right_front_direction, "out")
			f_write(self.__gpio_right_front_edge, "both")	
			
			f_write(GPIO_PATH + "/export", self.__gpio_right_back_num)
			f_write(self.__gpio_right_back_direction, "out")
			f_write(self.__gpio_right_back_edge, "both")	
			
			f_write(self.__pwm_left_request, "1")
			f_write(self.__pwm_left_run, "0")
			f_write(self.__pwm_left_period_freq, str(MTR_PWM_FREQ))
			f_write(self.__pwm_left_duty_ns, str(MTR_MIN_DUTY_NS))
			f_write(self.__pwm_left_run, "1")
			
			f_write(self.__pwm_right_request, "1")
			f_write(self.__pwm_right_run, "0")
			f_write(self.__pwm_right_period_freq, str(MTR_PWM_FREQ))
			f_write(self.__pwm_right_duty_ns, str(MTR_MIN_DUTY_NS))
			f_write(self.__pwm_right_run, "1")

			
	

	def move(self, units, direction):
		enc.pollEnc()
		f_write(self.__pwm_left_run, "0") # pwm left
		f_write(self.__pwm_right_run, "0") # pwm right
	
		enc.pollEnc()	
		f_write(self.__pwm_left_duty_ns, str(MTR_MAX_DUTY_NS)) # pwm left
		f_write(self.__pwm_right_duty_ns, str(MTR_MAX_DUTY_NS)) # pwm_right
		
		if(direction == 'forward'):
			f_write(self.__gpio_left_front_value, "0") # gpio left front
			f_write(self.__gpio_left_back_value, "1") # gpio left back
			f_write(self.__gpio_right_front_value, "0") # gpio right front
			f_write(self.__gpio_right_back_value, "1") # gpio right back
		elif(direction == 'backward'):
			f_write(self.__gpio_left_front_value, "1") # gpio left front
			f_write(self.__gpio_left_back_value, "0") # gpio left back
			f_write(self.__gpio_right_front_value, "1") # gpio right front
			f_write(self.__gpio_right_back_value, "0") # gpio right back
		elif(direction == 'right'):
			f_write(self.__gpio_left_front_value, "1") # gpio left front
			f_write(self.__gpio_left_back_value, "0") # gpio left back
			f_write(self.__gpio_right_front_value, "0") # gpio right front
			f_write(self.__gpio_right_back_value, "1") # gpio right back
		elif(direction == 'left'):
			f_write(self.__gpio_left_front_value, "0") # gpio left front
			f_write(self.__gpio_left_back_value, "1") # gpio left back
			f_write(self.__gpio_right_front_value, "1") # gpio right front
			f_write(self.__gpio_right_back_value, "0") # gpio right back
	
	
		
		encoders = enc.pollEnc()
		prev_left = encoders.Left
		prev_right = encoders.Right

		post_left = ctypes.c_uint32(prev_left + units).value
		post_right = ctypes.c_uint32(prev_right + units).value
		print "Moving prev " + hex(prev_left) + " post " + hex(post_left)
		f_write(self.__pwm_left_run, "1") # pwm left
		f_write(self.__pwm_right_run, "1") # pwm right
		
		end = 0
		while(end == 0):
			encoders = enc.pollEnc()
			curr_left = encoders.Left 
			curr_right = encoders.Right 
		
			if(curr_left >= post_left and curr_right >= post_right):
				end = 1
		
		f_write(self.__pwm_left_run, "0") # pwm left
		f_write(self.__pwm_right_run, "0") # pwm right
	
	def detach(self):
		f_write(self.__pwm_left_run, "0")
		f_write(self.__pwm_left_request, "0")
		
		f_write(self.__pwm_right_run, "0")
		f_write(self.__pwm_right_request, "0")
		
		f_write(GPIO_PATH + "/unexport", self.__gpio_left_front_num)
		f_write(GPIO_PATH + "/unexport", self.__gpio_left_back_num)
		f_write(GPIO_PATH + "/unexport", self.__gpio_right_front_num)
		f_write(GPIO_PATH + "/unexport", self.__gpio_right_back_num)
		
	def __del__(self):
		self.detach()	

# motor test
#ipwm.enable()

print 'Enabled motor'
mtr = Motor()
mtr.attach("P9_29", "P9_31", "49", "117", "115", "60")

os.system('./map')
enc.pollEnc()
enc.pollEnc()
#print 'Enabled prox'
#prox = Proximity()
#prox.attach("P9_16", "P9_29", "48")
#pipein = prox.start()

print 'Count 1'
count = 0
while count < 1:
	#val = os.read(pipein, 64)
	#print '1: count = %d\nval = %s\n' % (count, val)
	mtr.move(3, "left")
	mtr.move(3, "right")
	count = count + 1

#prox.stop()
#prox.detach()

#print 'Enabled claw'
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

print 'Count 2'
#count = 0
#while count < 40:
#	#val = os.read(pipein, 64)
	#print '2: count = %d\nval = %s\n' % (count, val)
#	mtr.move(3, "left")
#	mtr.move(3, "right")
#	count = count + 1

#prox.stop()
#prox.detach()

mtr.detach()
print "done killin!"
