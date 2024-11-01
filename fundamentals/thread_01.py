import threading
import time

# Variable global para almacenar el tiempo transcurrido
elapsed_time = 0
stop_timer = False

def timer():
    global elapsed_time
    global stop_timer
    while not stop_timer:
        time.sleep(1)
        elapsed_time += 1

if __name__ == "__main__":
    # Crear y empezar el hilo del contador
    timer_thread = threading.Thread(target=timer)
    timer_thread.start()

    # Pedir input al usuario
    user_input = input("Introduce algo y presiona Enter: ")

    # Detener el contador
    stop_timer = True

    # Esperar a que el hilo termine
    timer_thread.join()

    # Mostrar el tiempo transcurrido
    print(f"Has tardado {elapsed_time} segundos en introducir: {user_input}")
