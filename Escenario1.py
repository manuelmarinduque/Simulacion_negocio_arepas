# -*- coding: utf-8 -*-

"""
Integrantes:
Victor Manuel Marín Duque - 201556071
Yesid Fernando Andica - 201556001
Stiven Sepulveda Cano - 201556087
"""

import random
import simpy
import numpy as np

# Datos de la simulación
SEMILLA = 42
TIEMPO_TRABAJO = 480

# Variables desempeño
COLA = 0
MAX_COLA = 0
ESPERA_CLIENTES = np.array([])
UTILIDAD = 0

# Función que provoca una interrupción (excepción) en el proceso 'llegada' 
# cuando el tiempo simulado alcance 480 UT (Unidades de tiempo, en minutos):
def finalizacion(env, cliente):
    yield env.timeout(TIEMPO_TRABAJO)
    cliente.action.interrupt()

class Cliente():

	# Constructor de la clase:
	def __init__(self, env, servidor):
		self.__env = env
		self.__mesero = servidor
		# Comienza el proceso 'llegada' cuando se crea una instancia de 'Cliente':
		self.action = env.process(self.__llegada())

	def __llegada(self):
		try:
			# Se generan 1000 clientes; dado que los eventos de llegada terminan al pasar 480 UT,
			# tal cantidad de clientes realmente no llegan al negocio:
			for i in range(1000):
				# Comienza el proceso 'cliente':
				env.process(self.__salida(f'{i}'))
				# Llegada de los clientes con una distribución exponencial con media de 4 minutos:
				tiempo_llegada = random.expovariate(1.0/4.0)
				# El proceso 'llegada' se queda esperando hasta que se active el evento Timeout al 
				# pasar el tiempo indicado por el valor de 'tiempo_llegada':
				yield self.__env.timeout(tiempo_llegada)
		# Se captura la excepción de interrupción para que no lleguen más clientes:
		except simpy.Interrupt:
			print('Ya no se reciben mas clientes')    
            
	def __salida(self, nombre):
    	# El cliente llega y se va cuando se le atiende:
		llegada = self.__env.now
		print(f'Al minuto{env.now:7.2f} llega el cliente {nombre}')

		# Variables globales:
		global COLA
		global MAX_COLA
		global ESPERA_CLIENTES
		global UTILIDAD

    	#Atendemos a los clientes (retorno del yield)
    	# El cliente ocupa al mesero:
		with self.__mesero.request() as req:

			# Se aumenta el tamaño de la cola si un/algún mesero está ocupado:
			COLA += 1
			if COLA > MAX_COLA:
				MAX_COLA = COLA
			
			print(f'Tamaño de la cola: {COLA}')

			# Si el mesero está ocupado atendiendo a otro cliente, el cliente actual espera
			# a que se desocupe y lo atienda:
			yield req
			# Una vez desocupado el mesero y empiece a atender el cliente, se disminuye la cola:
			COLA = COLA - 1
			# Se calcula el tiempo que esperó el cliente:
			espera = self.__env.now - llegada
			# El tiempo de espera se añade a una lista para poder calcular el tiempo promedio de espera:
			ESPERA_CLIENTES = np.append(ESPERA_CLIENTES, espera)
			print(f'Al minuto{env.now:7.2f} el cliente {nombre} es atendido, esperando{espera:7.2f} minutos en cola')

			# Elección de la arepa:
			arepas = ['no_pide', 'con_todo', 'con_morcilla', 'bebe']
			# El siguiente método 'choice' elige alguna de las 4 opciones de la lista 'arepas' 
			# con una probabilidad indicada en el parámetro 'p' respectivamente:
			val = np.random.choice(arepas, p=[0.15, 0.35, 0.25, 0.25])
			if val == 'no pide':
				print('El cliente no pidió')
				tiempo_atencion = random.expovariate(1.0/1.5)
				yield self.__env.timeout(tiempo_atencion)
			elif val == 'con_todo':
				UTILIDAD += 750
				tiempo_atencion = random.uniform(5, 10)
				print(f'El cliente pidió con todo, saldrá en los próximos {tiempo_atencion:7.2f} minutos')
				yield self.__env.timeout(tiempo_atencion)
			elif val == 'bebe':
				UTILIDAD += 550
				tiempo_atencion = random.uniform(3, 7)
				print(f'El cliente pidió para el bebé, saldrá en los próximos {tiempo_atencion:7.2f} minutos')
				yield self.__env.timeout(tiempo_atencion)
			else:
				UTILIDAD += 500
				tiempo_atencion = random.expovariate(1.0/6.0)
				print(f'El cliente pidió con morcilla, saldrá en los próximos {tiempo_atencion:7.2f} minutos')
				yield self.__env.timeout(tiempo_atencion)
			
			print(f'Al minuto{env.now:7.2f} sale el cliente {nombre}')


# Inicio de la simulación

print('Negocio de arepas. Escenario 1: El negocio contrata 2 meseros más, la jornada es de 8 horas')
# random.seed(SEMILLA)
env = simpy.Environment()
servidor = simpy.Resource(env, capacity=3)
cliente = Cliente(env, servidor)
env.process(finalizacion(env, cliente))
env.run()

print(f"Cola máxima {MAX_COLA}")
print(f'El tiempo promedio de espera es: {np.mean(ESPERA_CLIENTES):7.2f}')
print(f'La utilidad es {UTILIDAD}')
