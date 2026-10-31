#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import smbus2
import struct
import time

# Dirección I2C de la Raspberry Pi Pico
SLAVE_ADDR = 0x0A

# Inicializar el bus I2C
i2c = smbus2.SMBus(1)

# Archivo de bitácora
LOG_FILE = "bitacora-potencia.csv"


def readPower():
    try:
        # Leer 4 bytes enviados por el esclavo
        msg = smbus2.i2c_msg.read(SLAVE_ADDR, 4)
        i2c.i2c_rdwr(msg)

        # Convertir los bytes recibidos a float
        data = bytes(list(msg))
        pwr = struct.unpack('<f', data)[0]

        return pwr

    except Exception as e:
        print("Error al leer desde la Pico:", e)
        return None


def writePower(pwr):
    try:
        # Convertir el float en 4 bytes
        data = struct.pack('<f', pwr)

        # Enviar los 4 bytes al esclavo
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
        i2c.i2c_rdwr(msg)

        return True

    except Exception as e:
        print("Error al escribir hacia la Pico:", e)
        return False


def logData(requested, received):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as file:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{timestamp},{requested},{received}\n")
    except OSError as e:
        print("Error al guardar la bitácora:", e)


def main():
    print("Control de potencia por I2C")
    print("Dirección del esclavo: 0x0A")
    print("Introduce un valor entre 0 y 100.")
    print("Escribe 'salir' para terminar.\n")

    try:
        while True:
            entrada = input("Power? ").strip()

            if entrada.lower() == "salir":
                break

            try:
                power = float(entrada)
            except ValueError:
                print("Entrada inválida. Introduce un número.\n")
                continue

            if not 0 <= power <= 100:
                print("Valor inválido. El rango permitido es 0 a 100.\n")
                continue

            # Enviar la potencia solicitada
            if not writePower(power):
                print("No se pudo enviar el valor.\n")
                continue

            # Leer la respuesta del esclavo
            received = readPower()

            if received is None:
                print("No se recibió una respuesta válida.\n")
                continue

            print(f"\tPotencia enviada: {power:.2f}")
            print(f"\tRespuesta de la Pico: {received:.2f}")

            # Guardar los resultados
            logData(power, received)
            print()

    except KeyboardInterrupt:
        print("\nPrograma interrumpido.")

    finally:
        i2c.close()
        print("Bus I2C cerrado.")


if __name__ == '__main__':
    main()