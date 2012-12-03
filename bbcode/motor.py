import pwm
import select
import datetime
import time
import signal
import os
import ctypes
from collections import namedtuple
from mmap import mmap
import struct
import enc 

from pinout import *
from claw import Claw
from proximity import Proximity

#Motor specific PWM configuration
MTR_MIN_DUTY_NS = 0
MTR_MAX_DUTY_NS = 6000000 #2 ms
MTR_PWM_FREQ = 50 #hz 

Error = namedtuple('MoveError', 'Left Right Dir')
	
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
				
			val = f_read(self.__pwm_left_request)
			if val.find('free') < 0:
				raise Exception('Pin ' + self.__pwm_pin_left + ' is already in use')
			
			val = f_read(self.__pwm_right_request)
			if val.find('free') < 0:
				raise Exception('Pin ' + self.__pwm_pin_right + ' is already in use')
			
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

	def rotate(self, velocity):
		f_write(self.__pwm_left_run, "0") # pwm left
		f_write(self.__pwm_right_run, "0") # pwm right
	
		if(velocity > 0):
			#right
			f_write(self.__gpio_left_front_value, "1") # gpio left front
			f_write(self.__gpio_left_back_value, "0") # gpio left back
			f_write(self.__gpio_right_front_value, "0") # gpio right front
			f_write(self.__gpio_right_back_value, "1") # gpio right back
		elif(velocity < 0):
			#left
			f_write(self.__gpio_left_front_value, "0") # gpio left front
			f_write(self.__gpio_left_back_value, "1") # gpio left back
			f_write(self.__gpio_right_front_value, "1") # gpio right front
			f_write(self.__gpio_right_back_value, "0") # gpio right back
		
		if(velocity == 0):
			f_write(self.__pwm_left_run, "0") # pwm left
			f_write(self.__pwm_right_run, "0") # pwm right
		else:
			if(abs(velocity) > 100):
				velocity = 100
	
			duty_ns = (abs(velocity)/100.0) * MTR_MAX_DUTY_NS;
			print 'duty_ns = ' + str(int(duty_ns))
		
			f_write(self.__pwm_left_duty_ns, str(int(duty_ns))) # pwm left
			f_write(self.__pwm_right_duty_ns, str(int(duty_ns))) # pwm_right
		
			f_write(self.__pwm_left_run, "1") # pwm left
			f_write(self.__pwm_right_run, "1") # pwm right
			
	def move(self, units, direction):
		enc.setEnc(0xF0000000, 0xF0000000)

		f_write(self.__pwm_left_run, "0") # pwm left
		f_write(self.__pwm_right_run, "0") # pwm right
	
		enc.pollEnc()	
		f_write(self.__pwm_left_duty_ns, str(MTR_MAX_DUTY_NS)) # pwm left
		f_write(self.__pwm_right_duty_ns, str(MTR_MAX_DUTY_NS)) # pwm_right
		
		units_left = 0
		units_right = 0	
		if(direction == 'forward'):
			units_left = units
			units_right = units
			f_write(self.__gpio_left_front_value, "0") # gpio left front
			f_write(self.__gpio_left_back_value, "1") # gpio left back
			f_write(self.__gpio_right_front_value, "0") # gpio right front
			f_write(self.__gpio_right_back_value, "1") # gpio right back
		elif(direction == 'backward'):
			units_left = -1 * units
			units_right = -1 * units
			f_write(self.__gpio_left_front_value, "1") # gpio left front
			f_write(self.__gpio_left_back_value, "0") # gpio left back
			f_write(self.__gpio_right_front_value, "1") # gpio right front
			f_write(self.__gpio_right_back_value, "0") # gpio right back
		elif(direction == 'right'):
			units_left = -1 * units
			units_right = 1 * units
			f_write(self.__gpio_left_front_value, "1") # gpio left front
			f_write(self.__gpio_left_back_value, "0") # gpio left back
			f_write(self.__gpio_right_front_value, "0") # gpio right front
			f_write(self.__gpio_right_back_value, "1") # gpio right back
		elif(direction == 'left'):
			units_left = 1 * units
			units_right = -1 * units
			f_write(self.__gpio_left_front_value, "0") # gpio left front
			f_write(self.__gpio_left_back_value, "1") # gpio left back
			f_write(self.__gpio_right_front_value, "1") # gpio right front
			f_write(self.__gpio_right_back_value, "0") # gpio right back
		
		encoders = enc.pollEnc()
		prev_left = encoders.Left
		prev_right = encoders.Right

		post_left = ctypes.c_uint32(prev_left + units_left).value
		post_right = ctypes.c_uint32(prev_right + units_right).value
		
		f_write(self.__pwm_left_run, "1") # pwm left
		f_write(self.__pwm_right_run, "1") # pwm right
		
		end = 0
		while(end == 0):
			encoders = enc.pollEnc()
			curr_left = encoders.Left 
			curr_right = encoders.Right 
			
			if(direction == 'forward'):
				if(curr_left >= post_left or curr_right >= post_right):
					end = 1
			elif(direction == 'backward'):
				if(curr_left <= post_left or curr_right <= post_right):
					end = 1
			elif(direction == 'right'):
				if(curr_left <= post_left or curr_right >= post_right):
					end = 1
			elif(direction == 'left'):	
				if(curr_left >= post_left or curr_right <= post_right):
					end = 1
	
		error = Error(curr_left - post_left, curr_right - post_right, direction)		
		f_write(self.__pwm_left_run, "0") # pwm left
		f_write(self.__pwm_right_run, "0") # pwm right
		
		return error;
	
	def startForward(self, leftspeed, rightspeed):
		enc.setEnc(0xF0000000, 0xF0000000)

		f_write(self.__pwm_left_run, "0") # pwm left
		f_write(self.__pwm_right_run, "0") # pwm right
	
		duty_ns_left = (abs(leftspeed)/100.0) * MTR_MAX_DUTY_NS;
		duty_ns_right = (abs(rightspeed)/100.0) * MTR_MAX_DUTY_NS;
		print 'duty_ns = ' + str(int(duty_ns_left)) + ',' + str(int(duty_ns_right))
		
		f_write(self.__pwm_left_duty_ns, str(int(duty_ns_left))) # pwm left
		f_write(self.__pwm_right_duty_ns, str(int(duty_ns_right))) # pwm_right
		
		
		f_write(self.__gpio_left_front_value, "0") # gpio left front
		f_write(self.__gpio_left_back_value, "1") # gpio left back
		f_write(self.__gpio_right_front_value, "0") # gpio right front
		f_write(self.__gpio_right_back_value, "1") # gpio right back
		
		f_write(self.__pwm_left_run, "1") # pwm left
		f_write(self.__pwm_right_run, "1") # pwm right
		
	
	def adjustForward(self, leftspeed, rightspeed):

	
		duty_ns_left = (abs(leftspeed)/100.0) * MTR_MAX_DUTY_NS;
		duty_ns_right = (abs(rightspeed)/100.0) * MTR_MAX_DUTY_NS;
		print 'duty_ns = ' + str(int(duty_ns_left)) + ',' + str(int(duty_ns_right))
		
		f_write(self.__pwm_left_duty_ns, str(int(duty_ns_left))) # pwm left
		f_write(self.__pwm_right_duty_ns, str(int(duty_ns_right))) # pwm_right
	def stopForward(self):
		
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

#print 'Enabled motor'
#mtr = Motor()
#mtr.attach("P9_29", "P9_31", "49", "117", "115", "60")

#os.system('./map')
#enc.pollEnc()

#count = -100.0
#while count <= 100.0:
#	mtr.rotate(count)
#	time.sleep(0.5)
#	count += 10.0

#count = 0
#while count < 100:
#	error = mtr.move(40, "forward")
#	print  'Forward '
#	print error
#	print '\n'
#	print '\n'
#	time.sleep(1)
#	error = mtr.move(40, "backward")
#	print  'Backward '
#	print error
#	print '\n'
#	print '\n'
#	time.sleep(1)
#	error = mtr.move(80, "right")
#	print  'Right '
#	print error
#	print '\n'
#	print '\n'
#	time.sleep(1)
#	error = mtr.move(80, "left")
#	print  'Left '
#	print error
#	print '\n'
#	print '\n'
#	time.sleep(1)
#	count = count + 1

#mtr.detach()
#print "done killin!"
