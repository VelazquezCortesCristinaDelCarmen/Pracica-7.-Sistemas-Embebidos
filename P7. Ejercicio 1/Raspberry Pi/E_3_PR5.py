#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nombre del archivo: E_3_PR5.py
Descripción: Reproduce el video durante 20 segundos con control gradual de volumen:
             - 0 a 5 s: Fade-in (0% a 100%)
             - 5 a 15 s: Volumen máximo (100%)
             - 15 a 20 s: Fade-out (100% a 0%)
"""

import os
import time
import vlc

VID_PATH = "/home/pi/videos/video.mp4"

def run_experiment_3():
    player = vlc.MediaPlayer()

    if os.path.exists(VID_PATH):
        media_video = vlc.Media(VID_PATH)
        player.set_media(media_video)
        
        # Iniciar en volumen 0
        player.audio_set_volume(0)
        player.play()

        print("Iniciando video con Fade-in de volumen (5 segundos)...")
        # 1. Incremento de volumen (0 a 5 s -> 0% a 100%)
        for i in range(50):
            vol = int((i + 1) * 2)  # Pasos de 2% cada 0.1 s
            player.audio_set_volume(vol)
            time.sleep(0.1)

        print("Volumen al 100% durante 10 segundos...")
        player.audio_set_volume(100)
        time.sleep(10)

        print("Iniciando Fade-out de volumen (5 segundos)...")
        # 3. Decremento de volumen (15 a 20 s -> 100% a 0%)
        for i in range(50):
            vol = int(100 - (i + 1) * 2)  # Pasos de -2% cada 0.1 s
            player.audio_set_volume(max(0, vol))
            time.sleep(0.1)

        player.stop()

if __name__ == "__main__":
    run_experiment_3()