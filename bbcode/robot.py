import proximity 
import claw
import motor
import os
import enc
import udp
import pwm

MIN_BALL_AREA = 800
MAX_BALL_AREA = 80000

CAM_IMG_WIDTH = 718
CAM_IMG_HEIGHT = 478

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

						drive = ((abs(error_x)-10)* (90.0/229.0)) + 10
						if error_x > 10:
							self.__motor.rotate(drive)
						elif error_x < -10:
							self.__motor.rotate(-1 * drive)
						else:
							self.__motor.rotate(0)
				else:
					self.__motor.rotate(0)
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

robot.track()	
