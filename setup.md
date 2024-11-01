# <span style="color:green">Setup para Ubuntu</span>

## 1. Creación de entornos virtuales

>Para crear un entorno virtual en Ubuntu, sigue este tutorial:  
[Cómo crear un entorno virtual de Python en Ubuntu](https://www.arubacloud.com/tutorial/how-to-create-a-python-virtual-environment-on-ubuntu.aspx)
### En terminal:
 - **Cambiar a la carpeta donde se va a crear la nueva carpeta del nuevo entorno virtual:**
`cd /usr/Venvs`
- **Crear la nueva carpeta:**
`mkdir env1 o sudo mkdir env1`
- **Crear el nuevo entorno virtual:**
`sudo python3 -m venv env1`
- **Cambiar el propietario y permisos de la carpeta donde se guardan los entornos virtuales:**
`sudo chown -R carlos /usr/Venvs`
 - **Activar el entorno virtual:**
 `source /usr/Venvs/env1/bin/activate`
 - **Cambiar al directorio de trabajo:**
 `cd ~/Documents/projects/wifi_scan`
 - **Salir del entorno virtual:**
 `deactivate`
- **Borrar una carpeta:**
`sudo rm -R folder_name`
- **Si se queda un puerto abierto, para cerrarlo hay que encontrar el proceso que lo está usando:**
`sudo lsof -i :port`
- **Cerrar procesos:**
`sudo kill -9 PID`
- ***Dar permisos a carpetas y subcarpetas***
`sudo chmod -R 777 ~/Documents`
---

## 2. Cambiar propietario y permisos de acceso de la carpeta del entorno virtual

>Para cambiar los permisos de acceso a una carpeta en Ubuntu, revisa esta guía:  
[Cómo cambiar permisos y propiedad de carpetas](https://askubuntu.com/questions/6723/change-folder-permissions-and-ownership)

---

## 3. Dar permisos de root al usuario actual

>Si necesitas otorgar permisos de root al usuario actual, sigue las instrucciones de este tutorial:  
[Cómo añadir un usuario y conceder privilegios de root en Ubuntu 18.04](https://www.liquidweb.com/blog/add-user-grant-root-privileges-ubuntu-18-04/)

---

## 4. Ejecutar la aplicación

### En terminal:
 - **Para ejecutar la aplicación:**
``sudo `which python` wifi_gps_dash_scan.py``

---

## 5. Markdown Cheat Sheet

>[Guía rápida de Mark Down](https://www.markdownguide.org/cheat-sheet/)