#!/usr/bin/env python
# -*- coding: utf-8 -*-
# The client program sets up its socket differently from the way a server does. Instead of binding to a port and listening, 
# it uses connect() to attach the socket directly to the remote address.

import socket
import sys
import time
import random



# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

# After the connection is established, data can be sent through the socket with sendall() and received with recv(), just as in 
# the server.

# m = ['Politicas Scheduling PrioEx Memory MFU',\
# 			'QuantumV 1.000',\
# 			'RealMemory 3', \
# 			'SwapMemory 4',\
# 			'PageSize 1', \
# 			(0.000,'Create 2048 5 '), \
# 				(0.001,'Create 3072 6'), \
# 				(0.002,'Create 5000 6'), \
# 				(0.003, 'Address 2 4'),\
# 				(1.000,'Address 2 1023'), \
# 				(1.001, 'Fin 2'), \
# 				(2.000, 'Address 3 20'),\
# 				(2.001, 'Address 3 3000'), \
# 				(2.002, 'Address 3 4900'),\
# 				(3.000, 'Create 1024 4'), \
# 				(3.001, 'Address 3 10'),\
# 				(3.002,'Fin 3'), \
# 				(3.003,'Create 1024 2'), \
# 				(3.004,'Create 1024 3'), \
# 				(4.000,'Address 1 10'),\
# 				(4.001,'Fin 1'),\
# 				(4.002,'Fin 4'),\
# 				(4.003,'Fin 5'),\
# 				(4.004,'Fin 6'),\
# 				(4.005,'End')]

m = ['Politicas Scheduling PrioEx Memory MFU',\
			'QuantumV 1.000',\
			'RealMemory 3', \
			'SwapMemory 4',\
			'PageSize 1', \
			(0.000,'Create 2048 5 '), \
				(1.003, 'Address 1 4'),\
				(2.001,'Create 3072 6 '), \
				(4.005,'End')]

try:
    
	previousMsgTime = 0.0
	
	debug1 = True
    
    # Send data
	firstTime = True
	
	#simulation parameters
	for i in range(5):
		print >>sys.stderr, 'client sending "%s"' % m[i]
		sock.sendall (m[i])
		respuesta = sock.recv(256)
		print >>sys.stderr, 'client received "%s"' % respuesta
		
	# commands	
	for i in range(5,len(m)):
		
		if firstTime:
			firstTime = False
			initialTime = time.time()
		
		thisMsgTime = m[i][0]
				
		if thisMsgTime > previousMsgTime:
			sleepTime =  thisMsgTime - previousMsgTime
			if debug1: print >>sys.stderr, 'sleeptime', sleepTime
			time.sleep(sleepTime)
			
		if debug1: print >>sys.stderr, 'antes de calcular timedM', thisMsgTime	
		
		print >>sys.stderr, 'client sending "%s"' % m[i][1]
		
		sock.sendall(m[i][1])
		
		# Look for the response
		respuesta = sock.recv(256)
		print >>sys.stderr, 'client received "%s"' % respuesta
		timestamp = time.time() - initialTime
		previousMsgTime = timestamp
		if debug1: print >>sys.stderr, 'timestamp', timestamp
	#end for.
	sock.close()
		

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
