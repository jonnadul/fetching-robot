import ctypes
import time
import datetime
import proximity 
import claw
import motor
import os
import enc
import udp
import pwm

MIN_BALL_AREA = 800
MAX_BALL_AREA = 120000

CAM_IMG_WIDTH = 718.0
CAM_IMG_HEIGHT = 478.0
CAM_IMG_DEADZONE = 10.0
MOTOR_DRIVE_LO = 50.0
MOTOR_DRIVE_HI = 100.0
ENCODER_DEF = 0x40000000

class Robot:
	def robot_init(self):
		print 'Robot Init'
		pwm.enable()
		os.system('./map')
	
		#print 'Claw Init'
		#self.__claw = claw.Claw()
		#self.__claw.attach("P9_14")
			
		#print 'Proximity Sensor Init'
		#self.__prox =  proximity.Proximity()
		#self.__prox.attach("38", "P9_42", "48")
		
		print 'Motor Init'
		self.__motor = motor.Motor()
		self.__motor.attach("P9_29", "P9_31", "49", "117", "115", "60")
		
		print 'UDP Init'
		self.__udp = udp.PhoneStream()
		self.__udp.attach()

	def track(self):
		while 1:
			positions = self.__udp.getPacket()
			
			length = len(positions)
			if length > 0:
				last_pos = positions[length-1]
				if last_pos.ULX != -9999:
					width = last_pos.BRX - last_pos.ULX
					height = last_pos.BRY - last_pos.ULY
					
					area = width * height
					print 'Width = ' + str(width)
					print 'Height = ' + str(height)
					print 'Area = ' + str(area)
					
					if area > MIN_BALL_AREA and area < MAX_BALL_AREA:
						center = last_pos.ULX + (width/2.0)
						error_x = center - (CAM_IMG_WIDTH/2.0)
						
						print 'Center = ' + str(center)
						print 'Error = ' + str(error_x) 

						drive = ((abs(error_x)-CAM_IMG_DEADZONE)* ((MOTOR_DRIVE_HI-MOTOR_DRIVE_LO)/(CAM_IMG_WIDTH/2.0 - CAM_IMG_DEADZONE))) + MOTOR_DRIVE_LO
						if error_x > CAM_IMG_DEADZONE:
							self.__motor.rotate(drive)
						elif error_x < -1.0*CAM_IMG_DEADZONE:
							self.__motor.rotate(-1 * drive)
						else:
							self.__motor.rotate(0)
				else:
					self.__motor.rotate(0)
	def trackPID(self, modenum):
		error_last = 0
		time_last = datetime.datetime.now().microsecond/1000.0
		integral = 0
		#kp_hi = 0.1225
		#kp_lo = 0.06225
		kp_hi = 0.05
		kp_lo = 0.020
		kp_thresh = 100
		ki_thresh = 50
		ki_hi = 0.0008
		ki_lo = 0.00077
		maxint = 100000
		kd = 1
		x_goal = CAM_IMG_WIDTH/2.0 - 9.0
		errorlist = [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000] 
		while 1:
			positions = self.__udp.getPacket()
		        time = datetime.datetime.now().microsecond/1000.0   	
			length = len(positions)
			if length > 0:
				last_pos = positions[length-1]
				if last_pos.MODE != modenum:
					return 0
				if last_pos.ULX != -9999:
					width = last_pos.BRX - last_pos.ULX
					height = last_pos.BRY - last_pos.ULY
					
					area = width * height
					print 'Width = ' + str(width)
					print 'Height = ' + str(height)
					print 'Area = ' + str(area)
					
					if area > MIN_BALL_AREA and area < MAX_BALL_AREA:
						center = last_pos.ULX + (width/2.0)
						error_x = center - x_goal
						errorlist.pop(0)
						errorlist.append(abs(error_x))	
						dt = abs(time - time_last)
						
						if((error_x <= 0 and error_last >= 0) or (error_x >= 0 and error_last <= 0)):
							integral = 0  
							print 'RESET INT*****'
						else:
							integral += (error_x)*(dt)
							if(integral > maxint):
								integral = maxint
							elif(integral < -1.0*maxint):
								integral = -1.0*maxint
						deriv = (error_x - error_last) / dt;
							
						print 'Center = ' + str(center)
						print 'Error = ' + str(error_x) + '('+str(error_last)+')'
						print 'Deriv = ' + str(deriv*kd)
						if(abs(error_x) > kp_thresh):
							kp = kp_hi
						else:
							kp = kp_lo
					        if(abs(error_x) > ki_thresh):
							ki = ki_hi
						else:
							ki = ki_lo
						print 'Int = ' + str(integral*ki)
						if(abs(error_x) < 10):
							drive = 0;
							integral = 0;
							self.__motor.rotate(0)
							if(sum(errorlist) < 150):
								return 1
							else:
								print errorlist
								print 'ERR: ' + str(sum(errorlist))
						else:
							drive = kp*error_x + ki*integral +kd*deriv 
						error_last = error_x
						time_last = time
						#if error_x > CAM_IMG_DEADZONE:
						#	self.__motor.rotate(drive)
						#elif error_x < -1.0*CAM_IMG_DEADZONE:
						#	self.__motor.rotate(-1 * drive)
						#else:
						self.__motor.rotate(drive)
				else:
					self.__motor.rotate(0)
	def trackForward(self):
		error_last = 0
		integral = 0
		x_thresh = 0
		x_adj_scale = 0.2
		max_error = 70
		#y_goal = CAM_IMG_HEIGHT -20
		#top of image = bottom when camera upside down
		y_goal_top = CAM_IMG_HEIGHT/2.0 +10
		y_goal = 20 
		x_goal = CAM_IMG_WIDTH/2.0 - 15.0 
		def_speed = 44
		speed_left = def_speed
		speed_right = def_speed
		self.__motor.startForward(speed_left, speed_right) 
		while 1:
			positions = self.__udp.getPacket()
		        time = datetime.datetime.now().microsecond/1000.0   	
			length = len(positions)
			if length > 0:
				last_pos = positions[length-1]
				if last_pos.ULX != -9999:
					width = last_pos.BRX - last_pos.ULX
					height = last_pos.BRY - last_pos.ULY
					
					area = width * height
					print 'Width = ' + str(width)
					print 'Height = ' + str(height)
					print 'Area = ' + str(area)
					
					if area > MIN_BALL_AREA and area < MAX_BALL_AREA:
						center_x = last_pos.ULX + (width/2.0)
						center_y = last_pos.ULY + (height/2.0)
						ULY = last_pos.ULY
						BRY = last_pos.BRY
						error_x = center_x - x_goal 
							
						print 'Center = (' + str(center_x)+ ',' + str(center_y) + ')'
						print 'Upper Y = ' + str(ULY)
						print 'Bott Y = ' + str(BRY) + ' (' + str(y_goal_top) +')'
						print 'Error = ' + str(error_x) + '('+str(error_last)+')'
						if(error_x > max_error):
							return 2
						if(error_x > x_thresh):
							#positive = left when camera upside down
							speed_left = def_speed - x_adj_scale*abs(error_x)
							speed_right = def_speed + x_adj_scale*abs(error_x)
						elif(error_x < -1*x_thresh):
							speed_right = def_speed - x_adj_scale*abs(error_x)
							speed_left = def_speed + x_adj_scale*abs(error_x)
						else:
							speed_left = def_speed
							speed_right = def_speed
						if ULY > y_goal or BRY > y_goal_top:
							self.__motor.adjustForward(speed_left, speed_right) 
						else:
							self.__motor.stopForward()
							return 1
				else:
					self.__motor.adjustForward(0,0)
	
	def explore(self, modenum):
		#print 'Proximity Sensor Init'
		self.__prox =  proximity.Proximity()
		self.__prox.attach("38", "P9_42", "48")
		
		while 1:	
			positions = self.__udp.getPacket()
			length = len(positions)
			if length > 0:
				last_pos = positions[length-1]
				if last_pos.MODE != modenum:
					self.__prox.detach()
					return 0
			read_count = 1
				
			pipein = self.__prox.start()
			
			dist_rght = []
			dist_left = []
			dist_cntr = []
				
			print 'Start count!'	
			while read_count < 12:
				obs = os.read(pipein, 64)
				pos = obs[0:4]
			
				if pos == 'rght':
					print 'Right'
					print "obs = " + obs[4:]
					dist_rght.append(obs[4:])
				elif pos == 'left':
					print 'Left'
					print "obs = " + obs[4:]
					dist_left.append(obs[4:])
				elif pos == 'cntr':
					print 'Center'
					print "obs = " + obs[4:]
					dist_cntr.append(obs[4:])
				
				read_count += 1
		
			self.__prox.stop()
			
			count_rght = 0
			count_cntr = 0
			count_left = 0

			for rght in dist_rght:
				if int(rght) > 0 and int(rght) <= 5500:
					count_rght = count_rght + 1
			
			for cntr in dist_cntr:
				if int(cntr) > 0 and int(cntr) <= 5500:
					count_cntr = count_cntr + 1
			
			for left in dist_left:
				if int(left) > 0 and int(left) <= 5500:
					count_left = count_left + 1
			
			print "count_rght " + str(count_rght)
			print "count_cntr " + str(count_cntr)
			print "count_left " + str(count_left)
		
			if (count_cntr == 0) or (count_cntr < count_rght and count_cntr < count_left):
				print "Going Center!"
				self.__motor.move(100, 'forward')
			elif (count_rght == 0) or (count_rght < count_cntr and count_rght < count_left):
				print "Going Right!"
				self.__motor.move(150,'left')
			elif (count_left == 0) or (count_left < count_cntr and count_left < count_rght):
				print "Going Left!"
				self.__motor.move(150,'right')
			else:
				print "Rescanning"
			
	def getUDP(self):	
		positions = self.__udp.getPacket()
		return positions			 
	def returnBack(self, encoders):
		os.system('./map')
		goal = ctypes.c_uint32(encoders.Left - 0xf0000000).value + ctypes.c_uint32(encoders.Right - 0xf0000000).value
		goal = goal/2
		self.__motor.move(goal, 'backward')
		
	def robot_kill(self):
		self.__claw.detach()
		self.__prox.detach()
		self.__motor.detach()
	
	def __del__(self):
		self.robot_kill()

robot = Robot()
print 'Init robot'
robot.robot_init()
print 'Done robot init'
while 1:
	positions = robot.getUDP()
	length = len(positions)
	print str(length) + 'packets returned'
	if length > 0:
		last_pos = positions[length-1]
		if last_pos.MODE == 1:
			# track
			os.system('./map')
			robot.trackPID(last_pos.MODE)	
		elif last_pos.MODE == 2:
			print '****fetch mode'
			if 1:
				# tracking test
				robot = Robot()
				robot.robot_init()
				theclaw = claw.Claw()
				theclaw.attach("P9_14")
				theclaw.openClaw()
				theclaw.detach()
				#trackpid rotates until object in center
				os.system('./map')
				#while 1:
				#print 'tracking'
				#while 1:
				code = robot.trackPID(last_pos.MODE)	
				if code==1:
					code2 = robot.trackForward()
					if code2 == 1:
						encoders = enc.pollEnc()
						print encoders
						theclaw.attach("P9_14")
						theclaw.closeClaw(100)
						theclaw.detach()
						robot.returnBack(encoders)
						time.sleep(0.5)
						theclaw.attach("P9_14")
						theclaw.openClaw()
						theclaw.detach()
						print 'End'
		elif last_pos.MODE == 3:
			#wall
			robot.explore(last_pos.MODE)
		else:
			print 'sleep'
			time.sleep(1)
if 0:
	# exploring test
	robot = Robot()
	robot.robot_init()
	robot.explore()
