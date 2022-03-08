
import simpy
import random
import math

def Proceso(nombre,env,llegada_time,CPU,ready,waiting,RAM):
    global lista
    global tiempEjec
    
    lista = []
    
    # Marca evento de llegada
    yield env.timeout(llegada_time)
    
    #hora a la que llega el proceso
    horaLlegada = env.now
    print ('%s llega a las %f ' % (nombre,horaLlegada))
    
    # memoria que puede necesitar cada proceso
    memoria = random.randint(1, 10)
    
    # cantidad de instrucciones que le pedira al cpu
    inst = random.randint(1, 10)
    print ('%s tiene %f instrucciones' % (nombre,inst))
    
    with RAM.get(memoria) as espacio: # intento decir que si hay suficiente memoria entonces se encole (entre a la cola)
        print ('%s utiliza %f de RAM' % (nombre,memoria))
        
        yield espacio # se usa la memoria (se manda a llamar la funcion RAM.get)
        
        en_re = 2 # eleccion de entrar a cola ready
        
        while (inst>0):
            print ('%s comienza a hacer cola para ready' % (nombre))
            
            if (en_re == 2):
                # pregunta si puede entrar a ready
                with ready.request() as read:
                    yield read # estamos en ready
                    print ('%s esta en Ready, esperando ser atendido por CPU' % (nombre))
                    with CPU.request() as cpu:
                        yield cpu # solo compruebo disponibilidad de CPU, no gasto tiempo
                
                # pregunta si CPU puede atender
                with CPU.request() as cpu:
                    print ('%s esta en CPU' % (nombre))
                    
                    yield cpu # se usa CPU
                    inst = inst -3
                    yield env.timeout(1) # al CPU le toma 1 unidad de tiempo hacer los 3 procesos
                    print ('%s sale de CPU a las %f de RAM' % (nombre,env.now))
                    print ('%s tiene %f instrucciones' % (nombre,inst))
                # saliendo de CPU
                
        
                if (inst >0): # entonces hay instrucciones faltantes
                    en_re = random.randint(1, 2) # escoge si volver a la cola ready o a operaciones de salida/entrada
                    # pregunta si puede entrar cola de ready
                else:
                    print ('%s no tiene mas instrucciones' % (nombre))
            
            if (en_re == 1): # escoge ir a cola de waiting
                print ('%s comienza a hacer cola para waiting' % (nombre))
                with waiting.request() as wait:
                    print ('%s esta en waiting' % (nombre))
                    yield wait
                    # tiempo que le toma hacer operaciones de entrada o salida. 1 o 2 u
                    op = random.randint(1, 2)
                    yield env.timeout(op)
                    
                    print ('%s sale de waiting a las %f de RAM' % (nombre,env.now))
                    print ('%s se tardo %f u de tiempo' % (nombre,op))
                    en_re = 2 # regresando a cola ready
    
    # -----Se termino el proceso 
    # Regresando memoria
    print ('%s termino su proceso' % (nombre))
    RAM.put(memoria)
    
    # tiempo de ejecucion del proceso
    tiempoTotal = env.now - horaLlegada
    
    # guarda tiempo de ejecucion de cada uno de los procesos
    lista.append(tiempoTotal)
    
    print ('%s se tardo %f' % (nombre, tiempoTotal))
    tiempEjec = tiempEjec + tiempoTotal
        
                
            
            
env = simpy.Environment() #ambiente de simulación
CPU = simpy.Resource(env,capacity = 1) # cola CPU running
ready = simpy.Resource(env,capacity = 1) # cola ready
waiting = simpy.Resource(env,capacity = 1) # cola waiting
RAM = simpy.Container(env, init=100, capacity=100) # cola new 


random.seed(10) # fijar el inicio de random

#tiempo_llegada = random.expovariate(1.0/10)

tiempEjec = 0
cantProcesos = 25 
for i in range(cantProcesos):
    env.process(Proceso('Proceso %d'%i,env,random.expovariate(1.0/10),CPU,ready,waiting,RAM))

env.run(until=1000)  #correr la simulación hasta el tiempo = 50

# promedio/media
media = tiempEjec/cantProcesos
print ("tiempo promedio por proceso es: ", media)

# Desviacion estandar
varianza = 0
for x in lista:
    varianza += (x-media)**2
    
desv = math.sqrt(varianza/cantProcesos)
print ("Desviacion estandar: ", desv)