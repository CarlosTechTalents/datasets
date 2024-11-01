import paramiko
import pandas as pd
import re
from datetime import datetime

# Configuración del router
router_ip = "192.168.1.1"
username = "root"
password = "Tech@123"
command = "gpsctl -ixtasuevpg"

# Función para ejecutar el comando y procesar la salida
def get_gps_data():
    # Configuración de cliente SSH
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Conectar y ejecutar comando
        ssh_client.connect(router_ip, username=username, password=password)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Obtener y decodificar la salida
        output = stdout.read().decode().splitlines()
        
    finally:
        ssh_client.close()

    # Convertir el diccionario a un DataFrame con una fila y columnas para cada valor
    df = pd.DataFrame([output], columns=["latitude", "longitude", "timestamp", "altitude", "status", "accuracy", "datetime", "speed", "satellites", "angle"])
    return df

# Llamada a la función y muestra del DataFrame
gps_data_df = get_gps_data()
print(gps_data_df)
