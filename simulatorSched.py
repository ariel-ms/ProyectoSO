#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket.

import socket
import sys
import time
import heapq

lista_procesos = {}
command_list = []
cola_listos = []
numero_id = 1
tam_memoria_real = 0
num_marcos_real = 0
tam_memoria_swap = 0
num_marcos_swap = 0
tam_pagina = 0

cpu = None
memoria_real = []
memoria_swapping = []

class Proceso: 
    def __init__(self, id_proceso, priori, tam, tiempo):
        self.id = id_proceso
        self.priori = priori
        self.tamano = tam
        self.tiempo = tiempo
        # #pagina (indice fila) | Bit residencia | Marco | Bit residencia swapping | Marco en Swapping
        self.tabla_paginas = [[None for x in range(4)] for y in range(tam / tam_pagina)]

    # def __cmp__(self, other):
    #     print(self.priori)
    #     return cmp((self.priori, self.tiempo), (other.priori, other.tiempo))

    def __lt__(self, other):
        return self.priori < other.priori

def get_marco_libre(memoria):
    for i in range(0, len(memoria)):
        if memoria[i] == None:
            return i
    return -1

def get_LRU():
    tiempo = sys.maxint
    lru = None
    indice = None
    for indice_marco in range(0, len(memoria_real)):
        marco = memoria_real[indice_marco]
        if marco[0] < tiempo:
            tiempo = marco[0]
            lru = marco
            indice = indice_marco
    return (indice, lru)

# busca el marco disponible, obtiene (p,d), pone en m
def carga_memoria(id_proceso, tupla):
    # busca marco disponible
    indice = get_marco_libre(memoria_real)

    # no hay marcos disponbles
    if indice == -1: 
        info_lru = get_LRU()
        #print("elem menos usado")
        #print(info_lru)
        #cargar en swap
        marco_en_swap = get_marco_libre(memoria_swapping)
        # se pone en swapping lo que estaba en real
        memoria_swapping[marco_en_swap] = info_lru[1]
        # actualizar indices de tabla procesos para indicar que esta en swapping
        lista_procesos[info_lru[1][1]].tabla_paginas[info_lru[1][1]][2] = 1
        lista_procesos[info_lru[1][1]].tabla_paginas[info_lru[1][1]][3] = marco_en_swap
        #poner None en ese marco de memoria real
        memoria_real[info_lru[0]] = None
        indice = get_marco_libre(memoria_real)
        # continuar ejeucion actual

    # (0, 1) - real | (2, 3) para swap

    # se coloca en memoria real (timestamp, id proceso, pagina del proceso)
    memoria_real[indice] = (time.time() - initialTime, id_proceso, tupla[0])
    # actualizacion del bit residencia
    lista_procesos[id_proceso].tabla_paginas[tupla[0]][0] = 1
    # poner numero de marco en tabla
    lista_procesos[id_proceso].tabla_paginas[tupla[0]][1] = indice

def getPageOffset(dir_virtual):
    p = dir_virtual / tam_pagina
    d = dir_virtual % tam_pagina
    return (p, d) 

def toCPU(cola_listos):
    print("ENTRE AL CPU")
    global cpu
    # proceso = sacar elem del heap
    proceso = heapq.heappop(cola_listos)
    tupla = getPageOffset(0)
    carga_memoria(proceso.id, tupla)
    #entra al cpu
    cpu = proceso

# regresar numero real
def get_dir_real(id_proceso, dir_virtual):
    tupla = getPageOffset(dir_virtual)

    # bit de residencia 0
    if lista_procesos[id_proceso].tabla_paginas[tupla[0]][0] == 0:
        # checar si esta en swapping
        if lista_procesos[id_proceso].tabla_paginas[tupla[0]][2] == 1:
            # obtener marco en swap (temp)
            marco_en_swap = lista_procesos[id_proceso].tabla_paginas[tupla[0]][3]
            # ya no esta en swapping
            lista_procesos[id_proceso].tabla_paginas[tupla[0]][2] = None
            # poner none en swap
            memoria_swapping[marco_en_swap] = None

        print("bit residencia fue 0 -- cargando")
        carga_memoria(id_proceso, tupla)

    # bit de residencia = 1
    if lista_procesos[id_proceso].tabla_paginas[tupla[0]][0] == 1:
        marco =  lista_procesos[id_proceso].tabla_paginas[tupla[0]][1]
        return marco*tam_pagina + tupla[1]
        # actualizar el tiempo

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
        print >>sys.stderr, 'server received "%s"' % data
        if data:
            print >>sys.stderr, 'sending answer back to the client'
            connection.sendall('process created')
            command_list = data.split()

            if command_list[0] == "RealMemory":
                tam_memoria_real = int(command_list[1])
            elif command_list[0] == "SwapMemory":
                tam_memoria_swap = int(command_list[1])
            elif command_list[0] == "PageSize":
                tam_pagina = int(command_list[1]) * 1024
                num_marcos_real = (tam_memoria_real*1024) / tam_pagina
                num_marcos_swap = (tam_memoria_swap*1024) / tam_pagina
                memoria_real = [None]*num_marcos_real
                memoria_swapping = [None]*num_marcos_swap

            if command_list[0] == "Create":
                print(command_list)
                tamano = int(command_list[1])
                prioridad = int(command_list[2])
                proceso_i = Proceso(numero_id, -1*prioridad, tamano, time.time() - initialTime)
                heapq.heappush(cola_listos, proceso_i)
                lista_procesos[numero_id] = proceso_i
                numero_id = numero_id + 1
                if cpu == None: 
                    toCPU(cola_listos)
                elif -1*proceso_i.priori > -1*cpu.priori:
                    # prempt
                    print("prempt")
                    temporal = cpu
                    toCPU(cola_listos)
                    # regresar proceso a cola de listos
                    heapq.heappush(cola_listos, temporal)
            elif command_list[0] == "Address":
                # si pagina no esta en real primero buscar en area swapp
                if int(command_list[1]) == cpu.id:
                    real = get_dir_real(int(command_list[1]), int(command_list[2]))
                    print("DIR REAL: " + str(real))
                    print(cpu.id)
        else:
            print >>sys.stderr, 'no data from', client_address
            connection.close()
            sys.exit()

finally:
     # Clean up the connection
    print >>sys.stderr, 'se fue al finally'
    for i in range(0, len(cola_listos)):
        elem = heapq.heappop(cola_listos)
        print(str(elem.id) + " - " + str(elem.priori) + " " + str(elem.tiempo))
    for i in range(0, len(memoria_real)):
        if memoria_real[i] != None:
            print "marco en real: " + str(i)
            print memoria_real[i]
    for i in range(0, len(memoria_swapping)):
        if memoria_swapping[i] != None:
            print "marco en swap: " + str(i)
            print memoria_swapping[i]
    connection.close()

#When communication with a client is finished, the connection needs to be cleaned up using close(). This example uses a try:finally block to ensure that close() is always called, even in the event of an error.

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))