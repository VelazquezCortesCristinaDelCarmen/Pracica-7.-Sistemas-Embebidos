from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Pines conectados a los 7 LEDs (según subsección 3.1.1)
LEDS = [12, 16, 18, 22, 24, 26, 32]

# Configurar todos los pines como salidas iniciadas en LOW
for pin in LEDS:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

try:
    while True:
        sleep(0.5)
        # Encender todos los LEDs
        for pin in LEDS:
            GPIO.output(pin, GPIO.HIGH)

        sleep(0.5)
        # Apagar todos los LEDs
        for pin in LEDS:
            GPIO.output(pin, GPIO.LOW)
except KeyboardInterrupt:
    GPIO.cleanup()