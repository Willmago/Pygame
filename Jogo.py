# --- Importa e inicia pacotes
import pygame
from config import *
from telas import init_screen, game_screen, win_screen
from boss_2 import *
from fase_boss3 import boss3_screen
from os import path

# --- Loop geral do jogo
music('intro.mp3', 0.2)
while state != QUIT:

    # Controle de FPS
    clock.tick(FPS)

    # -- Telas do jogo
    if state == INIT:
        state = init_screen(window)

    elif state == MAUA:
        state = game_screen(window, MAP, state)
    # - Tela segundo chefe
    elif state == JARE_GV:
        state = boss_2()
    # - Tela terceiro chefe
    elif state == BOSS3:
        state = boss3_screen(window, hp_imgs)

    elif state == WIN:
        state = win_screen(window)

pygame.quit()
