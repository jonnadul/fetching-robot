from struct import *
import socket
UDP_PORT = 54259

class PhoneStream:
	def attach(self):
		self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

		try:
			self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		except AttributeError:
     			pass
		self.__sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
		self.__sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

		self.__sock.bind(('', 54259))
		host = socket.gethostbyname(socket.gethostname())
		self.__sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
		self.__sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, 
                   socket.inet_aton('224.1.1.1') + socket.inet_aton(host))
		self.__sock.setblocking(0)

		#sock.bind(('localhost',UDP_PORT))
	#while True:
	def getPacket(self):
		numrecvd = 0
		numvalid = 0
		while 1:
			try:	
				data, addr = self.__sock.recvfrom(1024)
			#print "received message:", data
				ulx,uly,brx,bry = unpack('!llll',data[0:16])
				numrecvd += 1 
				if ulx != -9999:
					numvalid +=1
				print str(ulx), str(uly), str(brx), str(bry)
			except socket.error as msg:
				print 'Rec: ' + str(numrecvd) + ' Val: ' + str(numvalid)
				return
