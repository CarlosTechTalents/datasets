import paramiko
import json

# Configuración del router
router_ip = "192.168.1.1"
username = "root"
password = "Tech@123"
command = "gsmctl -E"

# Función para ejecutar el comando y obtener datos JSON
def get_modem_info():
    # Configuración del cliente SSH
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Conectar y ejecutar el comando
        ssh_client.connect(router_ip, username=username, password=password)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        
        # Leer y decodificar la salida
        output = stdout.read().decode()
                
    finally:
        ssh_client.close()
    
    return output

# Llamada a la función y presentación de la información en formato JSON
modem_info = get_modem_info()
print(modem_info)
