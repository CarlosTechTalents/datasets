import subprocess
import re
import os

def scan_wifi(interface):
    # Ejecuta el comando 'iwlist' para escanear redes WiFi
    try:
        print (interface)
        scan_output = subprocess.check_output(["sudo", "iwlist", interface, "scan"], universal_newlines=True)
        # print (scan_output)
    except subprocess.CalledProcessError as e:
        print("Error al escanear redes WiFi:", e)
        return []

    # Expresiones regulares para capturar SSID, BSSID (Address), y RSSI (Signal level)
    ssid_re = re.compile(r'ESSID:"([^"]*)"')
    bssid_re = re.compile(r'Address: ([0-9A-Fa-f:]{17})')
    rssi_re = re.compile(r'Signal level=(-?\d+)')

    # Listas para almacenar la información
    ssids = ssid_re.findall(scan_output)
    bssids = bssid_re.findall(scan_output)
    rssi_levels = rssi_re.findall(scan_output)

    # Empareja la información y devuélvela como una lista de diccionarios
    wifi_networks = []
    for i in range(min(len(ssids), len(bssids), len(rssi_levels))):
        wifi_networks.append({
            'SSID': ssids[i],
            'BSSID': bssids[i],
            'RSSI': int(rssi_levels[i])
        })

    return wifi_networks

if __name__ == "__main__":
    os.system ('clear')
    interface='wlp0s20f3'
    networks = scan_wifi(interface)
    if networks:
        for i, network in enumerate(networks, start=1):
            print(f"Red {i}:")
            print(f"  SSID:  {network['SSID']}")
            print(f"  BSSID: {network['BSSID']}")
            print(f"  RSSI:  {network['RSSI']} dBm")
    else:
        print("No se encontraron redes WiFi.")
