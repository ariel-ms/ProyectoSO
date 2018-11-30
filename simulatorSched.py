#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket.

import socket
import sys
import time
import heapq

command_list = []
cola_listos = []
numero_id = 1

class Proceso:
    def __init__(self, id_proceso, prioridad, tiempo):
        self.id = id_proceso
        self.prioridad = prioridad
        self.tiempo = tiempo
        print("esta es la prioridad del proceso " + str(self.id) + "-" + str(self.prioridad))

    def __cmp__(self, other):
        return cmp((self.prioridad, self.tiempo), (other.prioridad, other.tiempo))


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Then bind() is used to associate the socket with the server address. In this case, the address is localhost, referring to the current server, and the port number is 10000.

# Bind the socket to the port
server_address = ('localhost', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

#Calling listen() puts the socket into server mode, and accept() waits for an incoming connection.

# Listen for incoming connections
sock.listen(1)


# Wait for a connection
print >>sys.stderr, 'waiting for a connection'
connection, client_address = sock.accept()

#accept() returns an open connection between the server and client, along with the address of the client. The connection is actually a different socket on another port (assigned by the kernel). Data is read from the connection with recv() and transmitted with sendall().

try:
    print >>sys.stderr, 'connection from', client_address
    initialTime = time.time()

    # Receive the data 
    while True:   
        data = connection.recv(256)
        command_list = data.split()
        if len(command_list) > 0  and command_list[0] == "Create":
            prioridad = int(command_list[2])
            proceso_i = Proceso(numero_id, -1*prioridad, time.time() - initialTime)
            heapq.heappush(cola_listos, proceso_i)
            numero_id = numero_id + 1
            print prioridad
        print >>sys.stderr, 'server received "%s"' % data
        if data:
            print >>sys.stderr, 'sending answer back to the client'
            connection.sendall('process created')
        else:
            print >>sys.stderr, 'no data from', client_address
            connection.close()
            sys.exit()

finally:
     # Clean up the connection
    print >>sys.stderr, 'se fue al finally'
    for i in range(0, len(cola_listos)):
        elem = heapq.heappop(cola_listos)
        print(str(elem.id) + " - " + str(elem.prioridad) + " " + str(elem.tiempo))
    connection.close()

#When communication with a client is finished, the connection needs to be cleaned up using close(). This example uses a try:finally block to ensure that close() is always called, even in the event of an error.

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

