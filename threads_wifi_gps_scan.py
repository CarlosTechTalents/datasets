import subprocess
import re
import os

import pandas as pd

from time import sleep
from time import time
import datetime
from datetime import datetime as dt
from threading import Thread
import serial
# serial.tools is part of the pyserial library
from serial.tools import list_ports

from gps import Gps
from wifi import Wifi
import wifi

# Variables globales
stop_gps = False
df = pd.DataFrame()
gps = Gps ()
wifi = Wifi()

# Lectura del GPS en otro hilo
def task_gps_read():
    global stop_gps
    global gps

    while not stop_gps:
        gps.get_position()

# Main
if __name__ == "__main__":

    frecuencia_muestreo = 2
    os.system('clear')

    # Preguntar por el puerto al que está conectado el GPS
    gps.get_serial_port()
    # Crear un hilo para leer el GPS de manera constante y actualizar las variables globales
    thread_gps = Thread(target=task_gps_read, args=())
    thread_gps.start()

    # Obtener el/los interfaces de red wifi
    wifi.get_interfaces()
    wifi.print_interfaces_list()

    # Obtener los datos de la wifi a la que esta conectado este ordenador
    wifi.get_current_wifi_info()
    wifi.print_current_wifi_info()


    # Escanear las redes wifi disponibles
    i = 0
    iteraciones = 10
    while not gps.position:
        print ('Esperando a que el GPS se posicione')
        sleep(1)

    while i < iteraciones:
        start = time()
        wifi.scan_wifi(gps.position)
        print(f'LECTURAS DEL GPS: {gps.counter}')
        gps.print_position()

        wifi.print_full_wifi_networks()
        wifi.print_wifi_networks()
        print(wifi.wifi_networks_pd)
        i += 1
        tiempo_escaneo = time()- start
        print (f'Duración del escaneo de wifis: {time()- start}sg.')
        if tiempo_escaneo < frecuencia_muestreo:
            sleep(frecuencia_muestreo-tiempo_escaneo)

    # Finalizar el hilo de lectura del GPS
    stop_gps = True
    print('Waiting for the thread...')
    thread_gps.join()
    print (gps.position)