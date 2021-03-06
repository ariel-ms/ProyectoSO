#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This sample program, based on the one in the standard library documentation, receives incoming messages and echos them back to the sender. It starts by creating a TCP/IP socket.
from tabulate import tabulate
import socket
import sys
import time
import heapq

lista_procesos = {}
command_list = []
cola_listos = []
procesos_terminados = []
numero_id = 1
tam_memoria_real = 0
num_marcos_real = 0
tam_memoria_swap = 0
num_marcos_swap = 0
tam_pagina = 0
table = []

cpu = None
memoria_real = []
memoria_swapping = []

class Proceso: 
    def __init__(self, id_proceso, priori, tam, tiempo):
        self.id = id_proceso
        self.priori = priori
        self.tamano = tam
        self.tiempo = tiempo
        self.tiempocpu = 0.0
        self.tiempoterminacpu = 0.0
        self.acumtiempo = 0.0
        self.turnaround = 0.0
        self.tiempoespera = 0.0
        # #pagina (indice fila) | Bit residencia | Marco | Bit residencia swapping | Marco en Swapping
        self.tabla_paginas = [[None for x in range(4)] for y in range(tam / tam_pagina)]
        self.page_faults = 0.0
        self.visita_pagina = 0.0

    # def __cmp__(self, other):
    #     print(self.priori)
    #     return cmp((self.priori, self.tiempo), (other.priori, other.tiempo))

    def __lt__(self, other):
        return self.priori < other.priori

    def setTiempoInicialCpu(self):
        self.tiempocpu = initialTime
        #print 'cpu inicial time =  %s ms' % self.tiempocpu

    def setAcumTiempoCpu(self):
        difTiempo = time.time() - self.tiempocpu
        self.acumtiempo += difTiempo

    def printTiempoCpu(self):
        #print >>self.acumtiempo
        print 'cpu time =  %s ms' % self.acumtiempo
    
    def printTiempoTerminaCpu(self):
        self.tiempoterminacpu = time.time() - initialTime
        print 'cpu termina = %s ms' % self.tiempoterminacpu
    
    def setTurnaroud(self):
        #self.turnaround = time.time() - self.tiempo
        self.turnaround = self.acumtiempo + self.tiempoespera
    
    def printTurnaround(self):
        print 'turnaround =  %s ms' % self.turnaround

    def setTiempoEspera(self):
        self.tiempoespera = (time.time() - initialTime) - self.acumtiempo
    
    def printTiempoEspera(self):
        print >>sys.stderr, 'tiempo espera =  %s ms' % self.tiempoespera

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
    # se aumenta en uno el contador de page faults
    lista_procesos[id_proceso].page_faults += 1
    # actualizacion del bit residencia
    lista_procesos[id_proceso].tabla_paginas[tupla[0]][0] = 1
    # poner numero de marco en tabla
    lista_procesos[id_proceso].tabla_paginas[tupla[0]][1] = indice

def getPageOffset(dir_virtual):
    p = dir_virtual / tam_pagina
    d = dir_virtual % tam_pagina
    return (p, d) 

def toCPU(cola_listos):
    #print("ENTRE AL CPU")
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
"""
def finProceso(id_proceso):
    # 
    for i in memoria_real:
        #checar si esta en memoria real
        if lista_procesos[id_proceso] == memoria_real[i].id_proceso:
            memoria_real[i] = None
        # checar si esta en swapping
        elif lista_procesos[id_proceso] == memoria_swapping[i].id_proceso:
            memoria_swapping[i] = None
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
"""
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

    #print tabulate([['Comando','timestamp','dir real','cola de listos','CPU','Memoria','Swapping','Procesos Terminados']])
    headers = ['Comando','timestamp','dir real','cola de listos','CPU','Memoria','Swapping','Procesos Terminados']
    # Receive the data 
    while True:   
        data = connection.recv(256)
        #print >>sys.stderr, 'server received "%s"' % data
        if data:
            #print >>sys.stderr, 'sending answer back to the client'
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
                #print(command_list)
                tamano = int(command_list[1])
                prioridad = int(command_list[2])
                proceso_i = Proceso(numero_id, -1*prioridad, tamano, time.time() - initialTime)
                heapq.heappush(cola_listos, proceso_i)
                lista_procesos[numero_id] = proceso_i
                numero_id = numero_id + 1
                #proceso_i.tiempo = time.time()
                if cpu == None: 
                    #guarda el tiempo en el que entra al cpu
                    proceso_i.setTiempoInicialCpu()
                    toCPU(cola_listos)
                elif -1*proceso_i.priori > -1*cpu.priori:
                    # prempt
                    #print("prempt")
                    cpu.setAcumTiempoCpu()
                    #proceso_i.printTiempoCpu()
                    #cpu.printTiempoTerminaCpu()
                    #cpu.printTiempoCpu()
                    temporal = cpu
                    toCPU(cola_listos)
                    proceso_i.setTiempoInicialCpu()
                    # regresar proceso a cola de listos
                    heapq.heappush(cola_listos, temporal)
                #strings para la tabla
                cpustring = ''.join([str(cpu.id),"p",str(command_list[2])])

                colalistosstring = ''
                for i in range(0, len(cola_listos)):
                    colalistosstring += str(cola_listos[i].id) + "p" + str(-1*cola_listos[i].priori) + ", "
                
                memoriarealstring = ''  
                for i in range(0, len(memoria_real)):
                    if memoria_real[i] != None:
                        memoriarealstring += str(i) + ":"
                        memoriarealstring += str(memoria_real[i][1]) + "." + str(memoria_real[i][2]) + " ,"
                    else:
                        memoriarealstring += str(i)
                        memoriarealstring += ":L, "
                
                memoriaswapstring = ''
                for i in range(0, len(memoria_swapping)):
                    if memoria_swapping[i] != None:
                        memoriaswapstring += str(i) + ":"
                        memoriaswapstring += str(memoria_swapping[i][1]) + "." + str(memoria_swapping[i][2]) + " ,"
                    else:
                        memoriaswapstring += str(i)
                        memoriaswapstring += ":L, "
                
                #print tabulate([[data,time.time(),' ',colalistosstring , cpustring, memoriarealstring, memoriaswapstring,procesos_terminados]])
                table += [[data,str(time.time() - initialTime),' ',colalistosstring , cpustring, memoriarealstring, memoriaswapstring,str(procesos_terminados)]]
            elif command_list[0] == "Address":
                # si pagina no esta en real primero buscar en area swapp
                if int(command_list[1]) == cpu.id:
                    real = get_dir_real(int(command_list[1]), int(command_list[2]))
                    #print("DIR REAL: " + str(real))
                    #print(cpu.id)
                    lista_procesos[cpu.id].visita_pagina += 1
                #print tabulate([[data,time.time(),real,colalistosstring , cpustring, memoriarealstring, memoriaswapstring,procesos_terminados]])
                table += [[data,str(time.time() - initialTime),real,colalistosstring , cpustring, memoriarealstring, memoriaswapstring,str(procesos_terminados)]]
            #fin sacar de memoria real = none
            #sacar de mem virt. = none
            #array
            #tupla = timestamp , id_proceso, pag.
            #si id = idproceso -> none
            elif command_list[0] == "Fin":
                proceso_i.setAcumTiempoCpu()
                #proceso_i.printTiempoCpu()
                proceso_i.setTiempoEspera()
                #proceso_i.printTiempoEspera()
                proceso_i.setTurnaroud()
                #proceso_i.printTurnaround()
                procesos_terminados.append(command_list[1])
                #cpu = None       
                #print tabulate([[data,time.time(),' ',colalistosstring , cpustring, memoriarealstring, memoriaswapstring,procesos_terminados]])
                table += [[data,str(time.time() - initialTime),' ',colalistosstring , cpustring, memoriarealstring, memoriaswapstring,str(procesos_terminados)]]
            elif command_list[0] == "End":
                print "simulation terminated"
                for i in lista_procesos:
                    lista_procesos[i].setTiempoEspera()
                    lista_procesos[i].setTurnaroud()
        
        else:
            print >>sys.stderr, 'no data from', client_address
            connection.close()
            sys.exit()

finally:
    #print tabulate (table,headers)
    print tabulate(table, headers, tablefmt="fancy_grid")
    #print (table)
     # Clean up the connection
    # print >>sys.stderr, 'se fue al finally'
    # for i in range(0, len(cola_listos)):
    #     elem = heapq.heappop(cola_listos)
    #     print(str(elem.id) + " - " + str(elem.priori) + " " + str(elem.tiempo))
    # for i in range(0, len(memoria_real)):
    #     if memoria_real[i] != None:
    #         print "marco en real: " + str(i)
    #         print memoria_real[i]
    # for i in range(0, len(memoria_swapping)):
    #     if memoria_swapping[i] != None:
    #         print "marco en swap: " + str(i)
    #         print memoria_swapping[i]
    #imprime los tiempos para cada proceso
    suma_turnaround = 0
    suma_espera = 0
    for i in lista_procesos:
        print "Proceso %s" %i
        print ("tiempo de cpu: " + str(lista_procesos[i].acumtiempo))
        print ("tiempo de turnaround: " + str(lista_procesos[i].turnaround))
        print ("tiempo de espera: " + str(lista_procesos[i].tiempoespera))
        print ("page faults: " + str(lista_procesos[i].page_faults))
        print ("visitas pagina: " + str(lista_procesos[i].visita_pagina))
        print ("rendimiento: " + str(1 - (lista_procesos[i].page_faults/lista_procesos[i].visita_pagina)))
        suma_turnaround += lista_procesos[i].turnaround
        suma_espera += lista_procesos[i].tiempoespera

    print("turnaround promedio: " + str(suma_turnaround/len(lista_procesos)))
    print("espera promedio: " + str(suma_espera/len(lista_procesos)))
    connection.close()

#When communication with a client is finished, the connection needs to be cleaned up using close(). This example uses a try:finally block to ensure that close() is always called, even in the event of an error.

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))