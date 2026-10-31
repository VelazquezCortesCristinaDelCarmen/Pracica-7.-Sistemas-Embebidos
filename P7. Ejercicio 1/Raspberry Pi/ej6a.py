from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Lista de pines en el orden físico de la línea de LEDs
LEDS = [12, 16, 18, 22, 24, 26, 32]

for pin in LEDS:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

try:
    delay = float(
        input("Ingrese el tiempo de retardo entre LEDs en segundos: ")
    )

    while True:
        # IZQUIERDA → DERECHA (Recorre del índice 0 al último)
        for pin in LEDS:
            GPIO.output(pin, GPIO.HIGH)
            sleep(delay)
            GPIO.output(pin, GPIO.LOW)

        # DERECHA → IZQUIERDA
        # Se omite el primer y último elemento (LEDS[-2::-1]) para evitar
        # repetirlos en el punto de retorno y mantener el flujo continuo.
        for pin in LEDS[-2:0:-1]:
            GPIO.output(pin, GPIO.HIGH)
            sleep(delay)
            GPIO.output(pin, GPIO.LOW)

except (KeyboardInterrupt, ValueError):
    pass
finally:
    GPIO.cleanup()