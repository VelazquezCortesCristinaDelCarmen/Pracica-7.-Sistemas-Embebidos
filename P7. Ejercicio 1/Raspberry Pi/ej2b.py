from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

LEDS = [12, 16, 18, 22, 24, 26, 32]

for pin in LEDS:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)


# Función para mapear los 7 bits de un número a los pines del GPIO
def mostrar_patron(patron):
    for i in range(7):
        # Evalúa cada bit utilizando AND bit a bit (sin usar XOR)
        estado = GPIO.HIGH if (patron & (1 << i)) else GPIO.LOW
        GPIO.output(LEDS[i], estado)


try:
    while True:
        # Desplaza un solo bit encendido a la izquierda mediante corrimiento
        for i in range(7):
            patron = 1 << i
            mostrar_patron(patron)
            sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup()