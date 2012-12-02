import os
import udp
import time

phonestream = udp.PhoneStream()
phonestream.attach()
phonestream.getPacket() 

count = 0
while count < 32:
	phonestream.getPacket()
	time.sleep(0.1)
	count = count+1


