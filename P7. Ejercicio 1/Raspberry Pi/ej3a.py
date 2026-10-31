from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

LEDS = [12, 16, 18, 22, 24, 26, 32]

for pin in LEDS:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

try:
     delay = float(
        input("Ingrese el tiempo de retardo entre LEDs en segundos: ")
    )
    while True:
        # Encender secuencialmente de derecha a izquierda (recorriendo al revés)
        for pin in reversed(LEDS):
            GPIO.output(pin, GPIO.HIGH)
            sleep(delay)
            GPIO.output(pin, GPIO.LOW)
except (KeyboardInterrupt, ValueError):
    GPIO.cleanup()