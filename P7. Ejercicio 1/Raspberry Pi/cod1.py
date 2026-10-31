# Importa la librería de control del GPIO de la Raspberry Pi
import RPi.GPIO as GPIO

# Importa la función sleep del módulo time
from time import sleep

# Desactivar advertencias (warnings)
GPIO.setwarnings(False)

# Configurar la librería para usar el número de pin.
# Llame GPIO.setmode(GPIO.BCM) para usar el canal SOC definido por Broadcom
GPIO.setmode(GPIO.BOARD)

# Configurar el pin 32 como salida y habilitar en bajo
GPIO.setup(32, GPIO.OUT, initial=GPIO.LOW)

# El siguiente código hace parpadear el led
while True:  # Bucle infinito
    sleep(0.5)  # Espera 500ms
    GPIO.output(32, GPIO.HIGH)  # Enciende el led
    sleep(0.5)  # Espera 500ms
    GPIO.output(32, GPIO.LOW)  # Apaga el led