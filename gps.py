import subprocess
import re
import os

import pandas as pd

from datetime import datetime as dt
from datetime import timezone 
  
from threading import Thread
import serial
# serial.tools is part of the pyserial library
from serial.tools import list_ports

class Gps:
    def __init__(self):
        self.serial_port = ''
        self.line = ''
        self.position = ''
        self.computer_timestamp = 0
        self.counter = 0

    # Get USB port where GPS is connected
    def get_serial_port(self):
        ports = list(list_ports.comports())
        valid_ports = []
        for i, port in enumerate(ports):
            if port[1] != 'n/a':
                valid_ports.append(i)
                print(f"{i}=>{port[0]}-{port[1]}-{port[2]}")

        while True:
            try:
                # gps_port = int(input('Introduce el puerto del GPS :'))
                gps_port = 32
                if gps_port in valid_ports:
                    break
            except ValueError:
                print('Puerto no válido, inténtalo de nuevo: ')

        self.serial_port = serial.Serial(ports[gps_port].device, baudrate=9600, timeout=10.0)

    # Reset input buffer
    def gps_reset_input_buffer(self):
        self.serial_port.reset_input_buffer()
        
    # Lectura del GPS
    def get_position (self):
        self.counter += 1
        try:
            while True:
                self.line = self.serial_port.readline().decode('ascii', errors='replace').strip()
                if self.line.startswith('$GNGGA'):
                    self.computer_timestamp = dt.now().timestamp()
                    print (self.line)
                    self.position = parse_nmea_sentence(self)
                    return self.position
        except serial.SerialException as e:
            print(f"Error: {e}")
            return "Error"
        """
        except KeyboardInterrupt:
            print("Keyboard Interrupt. Exiting GPS read function...") 
            return "Interrupt"
        """
        
    # Imprimir lectura del GPS
    def print_position (self):
        print (f"\nPosición GPS:\n{self.position}")
        return None


# Transformación de la secuencia NMEA del GPS
def parse_nmea_sentence(self):
    parts = self.line.split(',')
    if len(parts) >= 6:
        gps_data={'UTC': parts[1],
                  'Latitude': convert_to_degrees(parts[2], parts[3]),
                  'Longitude': convert_to_degrees(parts[4], parts[5]),
                  'Orthometric Heigth': parts[9],
                  'Geoid Separation': parts[11],
                  'computer_timestamp': self.computer_timestamp,
                  'computer_time_local': dt.fromtimestamp(self.computer_timestamp, tz = None).strftime('%d/%m/%Y, %H:%M:%S.%f'),
                  'computer_time_utc': dt.fromtimestamp(self.computer_timestamp, tz = timezone.utc).strftime('%d/%m/%Y, %H:%M:%S.%f'),
                  'line': self.line}
        return gps_data

    return

# Conversión de coordenadas a grados decimales
def convert_to_degrees(value, direction):
    if not value or not direction:
        return None
    
    if direction in ['N', 'S']:
        degrees = float(value[:2])
        minutes = float(value[2:])
    else:
        degrees = float(value[:3])
        minutes = float(value[3:])

    decimal_degrees = degrees + minutes / 60
    if direction in ['S', 'W']:
        decimal_degrees = -decimal_degrees
    return decimal_degrees

