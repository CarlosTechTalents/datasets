import subprocess
import re
import os

def get_interface_details(interface):
    details = {}

    # Obtenemos detalles básicos con iwconfig
    try:
        iwconfig_output = subprocess.check_output(["iwconfig", interface], universal_newlines=True)
        details['iwconfig'] = iwconfig_output.strip()
    except subprocess.CalledProcessError:
        details['iwconfig'] = "No disponible"

    # Obtenemos detalles adicionales con ip link
    try:
        ip_link_output = subprocess.check_output(["ip", "link", "show", interface], universal_newlines=True)
        details['ip_link'] = ip_link_output.strip()
    except subprocess.CalledProcessError:
        details['ip_link'] = "No disponible"

    # Obtenemos detalles adicionales con nmcli (NetworkManager)
    try:
        nmcli_output = subprocess.check_output(["nmcli", "-t", "-f", "all", "device", "show", interface], universal_newlines=True)
        details['nmcli'] = nmcli_output.strip()
    except subprocess.CalledProcessError:
        details['nmcli'] = "No disponible"

    return details

def get_wifi_interfaces():
    try:
        # Ejecuta el comando 'iwconfig' para obtener información de todas las interfaces de red
        iwconfig_output = subprocess.check_output(["iwconfig"], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print("Error al obtener las interfaces de red:", e)
        return {}

    # Expresión regular para encontrar nombres de interfaces que tengan capacidades inalámbricas
    interface_re = re.compile(r'^(\w+)\s+IEEE\s+802\.11', re.MULTILINE)

    # Encuentra todos los nombres de interfaces WiFi
    wifi_interfaces = interface_re.findall(iwconfig_output)

    # Recoge los detalles de cada interfaz WiFi
    interfaces_details = {}
    for interface in wifi_interfaces:
        interfaces_details[interface] = get_interface_details(interface)

    return interfaces_details

if __name__ == "__main__":
    os.system('clear')
    interfaces = get_wifi_interfaces()

    if interfaces:
        print("Detalles de las interfaces de red WiFi encontradas:")
        for interface, details in interfaces.items():
            print(f"\nInterface: {interface}")
            print("=== iwconfig ===")
            print(details['iwconfig'])
            print("=== ip link ===")
            print(details['ip_link'])
            print("=== nmcli ===")
            print(details['nmcli'])
    else:
        print("No se encontraron interfaces de red WiFi.")
