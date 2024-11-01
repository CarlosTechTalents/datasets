import paramiko
import pandas as pd
import re

# Establecemos la configuración del router
router_ip = "192.168.1.1"
username = "root"
password = "Tech@123"
command = "iw wlan0 scan"

# Creamos una función para conectarse al router y ejecutar el comando
def get_wifi_networks():
    # Creamos el cliente SSH
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Nos conectamos al router
        ssh_client.connect(router_ip, username=username, password=password)
        
        # Ejecutamos el comando
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Obtenemos la salida del comando
        output = stdout.read().decode()
        
    finally:
        ssh_client.close()
    
    # Expresiones regulares para extraer los datos de cada red
    ssid_pattern = re.compile(r"SSID: (.+)")
    signal_pattern = re.compile(r"signal: (-\d+\.\d+) dBm")
    freq_pattern = re.compile(r"freq: (\d+)")
    
    networks = []
    
    # Dividimos la salida en bloques de red
    blocks = output.split("BSS ")
    
    for block in blocks[1:]:  # Saltamos el primer bloque que es solo metadata
        ssid_match = ssid_pattern.search(block)
        signal_match = signal_pattern.search(block)
        freq_match = freq_pattern.search(block)
        
        if ssid_match and signal_match and freq_match:
            ssid = ssid_match.group(1)
            signal = float(signal_match.group(1))
            freq = int(freq_match.group(1))
            networks.append({"ssid": ssid, "signal": signal, "freq": freq})
    
    # Convertimos los datos en un DataFrame
    df = pd.DataFrame(networks, columns=["ssid", "signal", "freq"])
    
    return df

# Ejecutamos la función y mostramos el DataFrame
wifi_networks_df = get_wifi_networks()
print(wifi_networks_df.sort_values(by=['signal'], ascending=False))
