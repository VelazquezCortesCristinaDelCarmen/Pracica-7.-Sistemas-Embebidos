from time import sleep
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

PIN_LED = 32
GPIO.setup(PIN_LED, GPIO.OUT, initial=GPIO.LOW)

# Frecuencia alta (1000Hz) para evitar parpadeo visible en variaciones de brillo
pwm = GPIO.PWM(PIN_LED, 1000)
pwm.start(0)

pasos = 100  # Resolución de 100 pasos por segundo
dt = 1.0 / pasos  # Intervalo de tiempo entre cada paso (0.01s)

try:
    while True:
        # 1. Encendido gradual durante 1 segundo (0% a 100%)
        for duty in range(0, 101):
            pwm.ChangeDutyCycle(duty)
            sleep(dt)

        # 2. Permanece encendido al 100% durante 0.5 segundos
        pwm.ChangeDutyCycle(100)
        sleep(0.5)

        # 3. Apagado gradual durante 1 segundo (100% a 0%)
        for duty in range(100, -1, -1):
            pwm.ChangeDutyCycle(duty)
            sleep(dt)

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()