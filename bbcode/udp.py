from struct import *
import socket
UDP_PORT = 54259

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

try:
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except AttributeError:
     pass
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

sock.bind(('', 54259))
host = socket.gethostbyname(socket.gethostname())
sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, 
                   socket.inet_aton('224.1.1.1') + socket.inet_aton(host))


#sock.bind(('localhost',UDP_PORT))
while True:
	data, addr = sock.recvfrom(1024)
	#print "received message:", data
	ulx,uly,brx,bry = unpack('!llll',data[0:16])
	print str(ulx), str(uly), str(brx), str(bry)
