import os
import udp
import time

phonestream = udp.PhoneStream()
phonestream.attach()
phonestream.getPacket() 

count = 0
while count < 32:
	positions = phonestream.getPacket()

	for position in positions:
		print position 
	time.sleep(0.1)
	count = count+1


