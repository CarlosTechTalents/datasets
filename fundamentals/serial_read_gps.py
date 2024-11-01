# serial.tools is part of the pyserial library
from serial.tools import list_ports
import serial
from colores import colores as clr

if __name__ == '__main__':

    ports = list(list_ports.comports())
    for i, port in enumerate(ports):
        print(f"{i}=>{port}")
        
    gps = int(input("Introduce el puerto del GPS :"))
        
    port = serial.Serial(ports[gps].device, baudrate=9600, timeout=10.0)

    line = ""
    position = []
    print("connected to: " + port.portstr)

    while True:
        try:
            rcv = str(port.read(),'utf-8')
            if ord(rcv) == 10:
                match line[3:6]:
                    case 'GGA':
                        color = clr.CYAN
                        position = line.split(',')
                        print(f"{clr.GREEN}{position}")
                    case 'GLL':
                        color = clr.PURPLE
                    case 'RMC':
                        color = clr.MUSTARD
                    case _:
                        color = clr.WHITE
                print(f"{color}:>{line}")
                line = ""
            elif  ord(rcv) != 13:
                line += rcv

        except:
            rcv = ''
