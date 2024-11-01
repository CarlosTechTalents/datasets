import subprocess
import re
import os

import pandas as pd
from io import StringIO

from datetime import datetime as dt
from datetime import timezone 

from threading import Thread
import serial
# serial.tools is part of the pyserial library
from serial.tools import list_ports


class Wifi:
    def __init__(self):
        self.interfaces = []
        self.connected_wifi = ''
        self.connected_wifi_info = {}
        self.wifi_networks = []
        self.wifi_networks_pd = pd.DataFrame()
        self.computer_timestamp = 0

    # Obtener interfaces de red wifi
    def get_interfaces (self):
        try:
            # Ejecuta el comando 'iwconfig' para obtener información de todas las interfaces de red
            iwconfig_output = subprocess.check_output(["iwconfig"], universal_newlines=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print("Error al obtener las interfaces de red:", e)
            self.interfaces = []
            return []

        # Expresión regular para encontrar nombres de interfaces que tengan capacidades inalámbricas (no muestran "no wireless extensions")
        interface_re = re.compile(r'^(\w+)\s+IEEE\s+802\.11', re.MULTILINE)

        # Encuentra todos los nombres de interfaces WiFi
        self.interfaces = interface_re.findall(iwconfig_output)

        return self.interfaces

    # Obtener los datos de la wifi a la que está conectado este dispositivo
    def get_current_wifi_info(self):
        try:
            # Ejecuta el comando 'iwconfig' para obtener información sobre la conexión WiFi actual
            self.connected_wifi = subprocess.check_output(["iwconfig", self.interfaces[0]], universal_newlines=True)
        except subprocess.CalledProcessError as e:
            print("Error al obtener la información de la red WiFi:", e)
            return None

        # Expresiones regulares para capturar SSID, BSSID (Access Point), y RSSI (Signal level)
        ssid_re = re.compile(r'ESSID:"([^"]*)"')
        bssid_re = re.compile(r'Access Point: ([0-9A-Fa-f:]{17})')
        rssi_re = re.compile(r'Signal level=(-?\d+)')

        # Encuentra los patrones en la salida del comando
        ssid_match = ssid_re.search(self.connected_wifi)
        bssid_match = bssid_re.search(self.connected_wifi)
        rssi_match = rssi_re.search(self.connected_wifi)

        if ssid_match and bssid_match and rssi_match:
            self.connected_wifi_info = {
                'SSID': ssid_match.group(1),
                'BSSID': bssid_match.group(1),
                'RSSI': int(rssi_match.group(1)),
                'iwconfig' : self.connected_wifi
            }
            return self.connected_wifi_info
        else:
            print("No se pudo obtener la información completa de la red WiFi conectada.")
            return None

    # Escanear las redes wifi dispoonibles
    def scan_wifi(self, gps):
        # Vacia la lista de redes wifi encontradas
        self.wifi_networks = []

        self.computer_timestamp = dt.now().timestamp()

        # Ejecuta el comando 'iwlist' para escanear redes WiFi
        try:
            scan_output = subprocess.check_output(["sudo", "iwlist", self.interfaces[0], "scan"], universal_newlines=True)

            scanned_network = ''

            # Expresiones regulares para capturar SSID, BSSID (Address), y RSSI (Signal level)
            ssid_re = re.compile(r'ESSID:"([^"]*)"')
            bssid_re = re.compile(r'Address: ([0-9A-Fa-f:]{17})')
            rssi_re = re.compile(r'Signal level=(-?\d+)')

            for line in scan_output.split('\n')[1:]:
                # Limpia datos deconocidos y primera linea
                if ('IE: Unknown:' not in line) and ('Scan completed' not in line):
                    # Detecta cuando hay una nueva red
                    if ('Cell' in line) and ('Cell 01' not in line):
                        ssid = ssid_re.findall(scanned_network)[0]
                        bssid = bssid_re.findall(scanned_network)[0]
                        rssi_level = int(rssi_re.findall(scanned_network)[0])

                        self.wifi_networks.append({'ssid':ssid,
                                                   'bssid':bssid,
                                                   'rssi':rssi_level,
                                                   'computer_timestamp': self.computer_timestamp,
                                                   'computer_time_local': dt.fromtimestamp(self.computer_timestamp, tz = None).strftime('%d/%m/%Y, %H:%M:%S.%f'),
                                                   'computer_time_utc': dt.fromtimestamp(self.computer_timestamp, tz = timezone.utc).strftime('%d/%m/%Y, %H:%M:%S.%f'),
                                                   'gps_utc': gps['UTC'],
                                                   'gps_latitude': gps['Latitude'],
                                                   'gps_longitude': gps['Longitude'],
                                                   'gps_orthometric_heigth': gps['Orthometric Heigth'],
                                                   'gps_geoid_separation': gps['Geoid Separation'],
                                                   'network_info':scanned_network,
                                                   'gps_info': gps['line']
                                                   })
                        scanned_network = ''
                    scanned_network += line + '\n'
            self.wifi_networks_pd = pd.DataFrame(self.wifi_networks).sort_values(by=['rssi','ssid'], ascending=False)

        except subprocess.CalledProcessError as e:
            print("Error al escanear redes WiFi:", e)

        return self.wifi_networks


    # Imprimir en el terminal la información de los interfaces de red
    def print_interfaces_list(self):
        if self.interfaces:
            print("Interfaces de red WiFi encontradas:")
            for i, interface in enumerate(self.interfaces, start=1):
                print(f"{i}. {interface}")
        else:
            print("No se encontraron interfaces de red WiFi.")

    # Imprimir en el terminal la información de la red wifi conectada
    def print_current_wifi_info(self):
        if self.connected_wifi_info:
            print("Información de la red WiFi actual:")
            print(f"  SSID:  {self.connected_wifi_info['SSID']}")
            print(f"  BSSID: {self.connected_wifi_info['BSSID']}")
            print(f"  RSSI:  {self.connected_wifi_info['RSSI']} dBm")
            print (f"  {self.connected_wifi_info['iwconfig']}")
        else:
            print("No se pudo obtener la información de la red WiFi actual.")


    # Imprimir en el terminal la información de las redes wifi disponibles
    def print_wifi_networks(self):

        if self.wifi_networks:
            for i, network in enumerate(self.wifi_networks, start=1):
                print(f"Red {i}: SSID: {network['ssid']}, BSSID: {network['bssid']}, RSSI: {network['rssi']} dBm")
        else:
            print("No se encontraron redes WiFi.")

    # Imprimir en el terminal la información completa de las redes wifi disponibles
    def print_full_wifi_networks(self):

        for i, network in enumerate(self.wifi_networks, start=1):
            for key, value in network.items():
                print (f'{key}: {value}')
