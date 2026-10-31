from machine import ADC
from utime import sleep_ms
import ustruct
from i2cslave import I2CSlave

VAREF = 2.7273
I2C_SLAVE_ADDR = 0x0A

def setup():
    global i2c, adcm, adcp
    i2c = I2CSlave(address=I2C_SLAVE_ADDR)
    adcm = ADC(0)  # Init ADC0
    adcp = ADC(1)  # Init ADC1

def read_temp():
    # Reads temperature in C from the ADC (read_u16 usa rango de 0 a 65535)
    vplus = adcp.read_u16()
    vminus = adcm.read_u16()
    vdiff = vplus - vminus
    temp = vdiff * VAREF / 655.35
    return temp

def main():
    setup()
    while True:
        # 1. Get temperature
        temperature = read_temp()
        
        # 2. Convert temperature from pyfloat to bytes
        data = ustruct.pack('<f', temperature)
        
        # 3. Check if Master requested data
        if i2c.waitForRdReq(timeout=0):
            # If so, send the temperature to Master
            i2c.write(data)
            
        # 4. Check if Master sent data
        if i2c.waitForData(timeout=0):
            rcv = i2c.read()
            print(rcv.decode('utf-8'))

if __name__ == '__main__':
    main()