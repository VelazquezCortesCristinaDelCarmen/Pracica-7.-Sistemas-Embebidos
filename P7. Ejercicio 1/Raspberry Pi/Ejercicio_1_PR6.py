# Ejercicio_1_PR6
import smbus2
import struct
import time

SLAVE_ADDR = 0x0A
LOG_FILE = './temp.log'
i2c = smbus2.SMBus(1)

def readTemperature():
    try:
        msg = smbus2.i2c_msg.read(SLAVE_ADDR, 4)
        i2c.i2c_rdwr(msg)
        data = list(msg)
        
        ba = bytearray()
        for c in data:
            ba.append(int(c))
            
        temp = struct.unpack('<f', ba)
        # CAMBIO: Retornamos el valor flotante extraído de la tupla para facilitar su uso
        return temp[0] 
    except:
        return None

def log_temp(temperature):
    try:
        # CAMBIO: Se cambió 'w+' a 'a' (append) para no sobreescribir y guardar el histórico.
        # CAMBIO: Se ajustó el formato a CSV (separado por coma) para facilitar la lectura posterior.
        with open(LOG_FILE, 'a') as fp:
            fp.write('{},{}\n'.format(time.time(), temperature))
    except:
        return

def main():
    while True:
        try:
            cTemp = readTemperature()
            if cTemp is not None:
                # CAMBIO: Imprimir en pantalla los valores de temperatura leídos [6pt]
                print(f"Temperatura registrada: {cTemp:.2f} °C")
                log_temp(cTemp)
            time.sleep(1)
        except KeyboardInterrupt:
            return

if __name__ == '__main__':
    main()