# Clase para definir colores de impresión en consola
class colores:
    RED = '\033[38;2;255;0;0m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    LIGHTCYAN = '\033[38;2;0;204;204m'
    GREEN = '\033[92m'
    YELLOWGREEN = '\033[38;2;102;204;0m'
    MUSTARD = '\033[38;2;153;153;0m'
    WHITE = '\033[38;2;220;220;220m'

    HEADER = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Código de prueba:
'''
print(f'{colores.RED}Tiempo de busqueda:')
print(f'{colores.PURPLE}Tiempo de busqueda:')
print(f'{colores.BLUE}Tiempo de busqueda:')
print(f'{colores.CYAN}Tiempo de busqueda:')
print(f'{colores.LIGHTCYAN}Tiempo de busqueda:')
print(f'{colores.GREEN}Tiempo de busqueda:')
print(f'{colores.YELLOWGREEN}Tiempo de busqueda:')
print(f'{colores.MUSTARD}Tiempo de busqueda:')
print(f'{colores.WHITE}Tiempo de busqueda:')
'''
