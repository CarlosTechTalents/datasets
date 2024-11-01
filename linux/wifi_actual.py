import subprocess
import re
import os

def get_current_wifi_info(interface=''):
    try:
        # Ejecuta el comando 'iwconfig' para obtener información sobre la conexión WiFi actual
        iwconfig_output = subprocess.check_output(["iwconfig", interface], universal_newlines=True)
        print(iwconfig_output)
    except subprocess.CalledProcessError as e:
        print("Error al obtener la información de la red WiFi:", e)
        return None

    # Expresiones regulares para capturar SSID, BSSID (Access Point), y RSSI (Signal level)
    ssid_re = re.compile(r'ESSID:"([^"]*)"')
    bssid_re = re.compile(r'Access Point: ([0-9A-Fa-f:]{17})')
    rssi_re = re.compile(r'Signal level=(-?\d+)')

    # Encuentra los patrones en la salida del comando
    ssid_match = ssid_re.search(iwconfig_output)
    bssid_match = bssid_re.search(iwconfig_output)
    rssi_match = rssi_re.search(iwconfig_output)

    if ssid_match and bssid_match and rssi_match:
        return {
            'SSID': ssid_match.group(1),
            'BSSID': bssid_match.group(1),
            'RSSI': int(rssi_match.group(1))
        }
    else:
        print("No se pudo obtener la información completa de la red WiFi.")
        return None

if __name__ == "__main__":
    os.system('clear')
    interface='wlp0s20f3'
    wifi_info = get_current_wifi_info(interface)

    if wifi_info:
        print("Información de la red WiFi actual:")
        print(f"  SSID:  {wifi_info['SSID']}")
        print(f"  BSSID: {wifi_info['BSSID']}")
        print(f"  RSSI:  {wifi_info['RSSI']} dBm")
    else:
        print("No se pudo obtener la información de la red WiFi actual.")
