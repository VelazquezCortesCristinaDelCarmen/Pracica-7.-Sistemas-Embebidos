#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nombre del archivo: E_4_PR5.py
Descripción: Controla la lista de reproducción mediante eventos de entrada GPIO
             utilizando la biblioteca RPi.GPIO (o gpiozero) en Raspberry Pi.
"""

import os
import time
import vlc
import RPi.GPIO as GPIO

# Mapeo de pines GPIO
PIN_PREV = 2
PIN_NEXT = 3
PIN_STOP = 4
PIN_PAUSE = 17
PIN_VOL_UP = 27
PIN_VOL_DOWN = 22

MEDIA_DIR = "/home/pi/videos"

class KioskController:
    def __init__(self, media_folder):
        self.instance = vlc.Instance()
        self.list_player = self.instance.media_list_player_new()
        self.player = self.list_player.get_media_player()
        
        # Crear lista de reproducción
        self.media_list = self.instance.media_list_new()
        files = [
            os.path.join(media_folder, f)
            for f in sorted(os.listdir(media_folder))
            if f.endswith(('.mp4', '.jpg', '.png'))
        ]
        
        for file in files:
            self.media_list.add_media(self.instance.media_new(file))
            
        self.list_player.set_media_list(self.media_list)
        self.volume = 70
        self.player.audio_set_volume(self.volume)

    def play(self):
        self.list_player.play()

    def previous(self, channel):
        print("GPIO Event: Anterior")
        self.list_player.previous()

    def next(self, channel):
        print("GPIO Event: Siguiente")
        self.list_player.next()

    def stop(self, channel):
        print("GPIO Event: Detener")
        self.list_player.stop()

    def toggle_pause(self, channel):
        print("GPIO Event: Pausar/Reanudar")
        self.list_player.pause()

    def volume_up(self, channel):
        self.volume = min(100, self.volume + 10)
        self.player.audio_set_volume(self.volume)
        print(f"GPIO Event: Volumen + ({self.volume}%)")

    def volume_down(self, channel):
        self.volume = max(0, self.volume - 10)
        self.player.audio_set_volume(self.volume)
        print(f"GPIO Event: Volumen - ({self.volume}%)")

def setup_gpio(kiosk):
    GPIO.setmode(GPIO.BCM)
    pins = [PIN_PREV, PIN_NEXT, PIN_STOP, PIN_PAUSE, PIN_VOL_UP, PIN_VOL_DOWN]
    
    for pin in pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Registro de interrupciones asociadas a los métodos del Kiosco
    GPIO.add_event_detect(PIN_PREV, GPIO.FALLING, callback=kiosk.previous, bouncetime=300)
    GPIO.add_event_detect(PIN_NEXT, GPIO.FALLING, callback=kiosk.next, bouncetime=300)
    GPIO.add_event_detect(PIN_STOP, GPIO.FALLING, callback=kiosk.stop, bouncetime=300)
    GPIO.add_event_detect(PIN_PAUSE, GPIO.FALLING, callback=kiosk.toggle_pause, bouncetime=300)
    GPIO.add_event_detect(PIN_VOL_UP, GPIO.FALLING, callback=kiosk.volume_up, bouncetime=300)
    GPIO.add_event_detect(PIN_VOL_DOWN, GPIO.FALLING, callback=kiosk.volume_down, bouncetime=300)

if __name__ == "__main__":
    if os.path.exists(MEDIA_DIR):
        kiosk = KioskController(MEDIA_DIR)
        setup_gpio(kiosk)
        kiosk.play()

        print("Sistema iniciado. Esperando pulsaciones en GPIO...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            GPIO.cleanup()