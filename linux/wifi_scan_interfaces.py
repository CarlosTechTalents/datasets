import subprocess
import re
import os

def get_wifi_interfaces():
    try:
        # Ejecuta el comando 'iwconfig' para obtener información de todas las interfaces de red
        iwconfig_output = subprocess.check_output(["iwconfig"], universal_newlines=True)
        print(iwconfig_output)
    except subprocess.CalledProcessError as e:
        print("Error al obtener las interfaces de red:", e)
        return []

    # Expresión regular para encontrar nombres de interfaces que tengan capacidades inalámbricas (no muestran "no wireless extensions")
    interface_re = re.compile(r'^(\w+)\s+IEEE\s+802\.11', re.MULTILINE)

    # Encuentra todos los nombres de interfaces WiFi
    wifi_interfaces = interface_re.findall(iwconfig_output)

    return wifi_interfaces

if __name__ == "__main__":
    os.system('clear')
    interfaces = get_wifi_interfaces()

    if interfaces:
        print("Interfaces de red WiFi encontradas:")
        for i, interface in enumerate(interfaces, start=1):
            print(f"{i}. {interface}")
    else:
        print("No se encontraron interfaces de red WiFi.")
