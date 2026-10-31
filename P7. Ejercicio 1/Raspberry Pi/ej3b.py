from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

LEDS = [12, 16, 18, 22, 24, 26, 32]

for pin in LEDS:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)


def mostrar_patron(patron):
    for i in range(7):
        estado = GPIO.HIGH if (patron & (1 << i)) else GPIO.LOW
        GPIO.output(LEDS[i], estado)


try:
    delay = float(
        input("Ingrese el tiempo de retardo entre LEDs en segundos: ")
    )
    while True:
        # Corrimiento de derecha a izquierda iniciando en el bit MSB (0x40 = 0b1000000)
        for i in range(6, -1, -1):
            patron = 1 << i
            mostrar_patron(patron)
            sleep(delay)
except (KeyboardInterrupt, ValueError):
    GPIO.cleanup()