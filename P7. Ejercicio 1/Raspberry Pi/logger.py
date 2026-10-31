#!/usr/bin/env python3
# Experimento 1: lee la temperatura del RP2040 por I2C, la imprime en pantalla
# y la guarda en la bitacora (una linea por lectura: "<timestamp_unix> <temp_C>").
import struct
import time
import smbus2

SLAVE_ADDR = 0x0A
LOG_FILE = './temp.log'

i2c = smbus2.SMBus(1)


def read_temperature():
    try:
        msg = smbus2.i2c_msg.read(SLAVE_ADDR, 4)
        i2c.i2c_rdwr(msg)
        raw = bytes(list(msg))
        return struct.unpack('<f', raw)[0]     # unpack devuelve tupla -> [0]
    except OSError:
        return None


def log_temp(temperature):
    with open(LOG_FILE, 'a') as fp:            # 'a' = acumula (antes 'w+' borraba todo)
        fp.write('{:.0f} {:.2f}\n'.format(time.time(), temperature))


def main():
    while True:
        try:
            t = read_temperature()
            if t is not None and -55.0 <= t <= 150.0:   # descarta lecturas fuera de rango
                print('Temperatura: {:.2f} C'.format(t))
                log_temp(t)
            else:
                print('Lectura invalida:', t)
            time.sleep(1)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
