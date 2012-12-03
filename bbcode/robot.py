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
		#self.__prox.attach("51", "P9_42", "48")
		
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
	def trackPID(self):
		error_last = 0
		time_last = datetime.datetime.now().microsecond/1000.0
		integral = 0
		kp_hi = 0.1225
		kp_lo = 0.06225
		kp_thresh = 100
		ki_thresh = 50
		ki_hi = 0.0008
		ki_lo = 0.00077
		maxint = 100000
		kd = 1
		x_goal = CAM_IMG_WIDTH/2.0 - 15.0 
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
						center = last_pos.ULX + (width/2.0)
						error_x = center - x_goal
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
							return
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
		y_goal_top = CAM_IMG_HEIGHT/3.0
		y_goal = 20 
		x_goal = CAM_IMG_WIDTH/2.0 - 15.0 
		def_speed = 34
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
						#if(error_x > max_error):
						#	return
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
							return
				else:
					self.__motor.adjustForward(0,0)
	def explore(self):
		end_loop = 0
		while not end_loop:
			# read udp stream to verify existance
			# of object of interest
		
			end_look = 0
			while not end_look:
		
				dist_left = []
				dist_rght = []
				dist_cntr = []
				read_count = 0
				
				pipein = self.__prox.start()
			
				print 'Start count!'	
				while read_count < 36:
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

				rght = 0
				left = 0
				cntr = 0
				for dist in dist_rght:
					if dist > 0 and dist < 4000:
						rght += 1
			 
				for dist in dist_left:
					if dist > 0 and dist < 4000:
						left += 1
			
				for dist in dist_cntr:
					if dist > 0 and dist < 4000:
						cntr += 1
			
				print 'rght = ' + str(rght)
				print 'left = ' + str(left)
				print 'cntr = ' + str(cntr)
				
				end_look = 1
			end_loop = 1
	def robot_kill(self):
		self.__claw.detach()
		self.__prox.detach()
		self.__motor.detach()
	
	def __del__(self):
		self.robot_kill()

robot = Robot()
robot.robot_init()

#robot.trackPID()	
robot.trackForward()
enc.pollEnc()
