import serial
# serial.tools is part of the pyserial library
from serial.tools import list_ports

def read_gps_data(serial_port):
    try:
        while True:
            line = serial_port.readline().decode('ascii', errors='replace').strip()
            if line.startswith('$GNGGA') or line.startswith('$GNRMC'):
                print(f"GPS Data: {line}")
                parse_nmea_sentence(line)
    except serial.SerialException as e:
        print(f"Error reading from {serial_port}: {e}")
    except KeyboardInterrupt:
        print("Exiting...")

def parse_nmea_sentence(nmea_sentence):
    if nmea_sentence.startswith('$GNGGA'):
        parts = nmea_sentence.split(',')
        if len(parts) >= 6:
            utc = parts[1]
            latitude = convert_to_degrees(parts[2], parts[3])
            longitude = convert_to_degrees(parts[4], parts[5])
            ortho_height = parts[9]
            geoid = parts[11]

            print(f"UTC: {utc}, Latitude: {latitude}, Longitude: {longitude}, Orthometric Heigth: {ortho_height}, Geoid Separation {geoid}")

def convert_to_degrees(value, direction):
    if not value or not direction:
        return None
    
    if direction in ['N', 'S']:
        degrees = float(value[:2])
        minutes = float(value[2:])
    else:
        degrees = float(value[:3])
        minutes = float(value[3:])

    decimal_degrees = degrees + minutes / 60
    if direction in ['S', 'W']:
        decimal_degrees = -decimal_degrees
    return decimal_degrees

if __name__ == "__main__":

    ports = list(list_ports.comports())
    valid_ports = []
    for i, port in enumerate(ports):
        if port[1] != 'n/a':
            valid_ports.append(i)
            print(f"{i}=>{port[0]}-{port[1]}-{port[2]}")

    while True:
        try:
            gps_port = int(input('Introduce el puerto del GPS :'))
            if gps_port in valid_ports:
                break
        except ValueError:
            print('Puerto no válido, inténtalo de nuevo: ')

        
    serial_port = serial.Serial(ports[gps_port].device, baudrate=9600, timeout=10.0)

    read_gps_data(serial_port)
