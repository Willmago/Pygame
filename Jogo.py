# --- Importa e inicia pacotes
import pygame
from config import *
from telas import init_screen, game_screen
from fase_boss3 import boss3_screen
from telas import init_screen, game_screen, win_screen

# --- Loop geral do jogo
music('intro.mp3', 0.2)
while state != QUIT:

    # Controle de FPS
    clock.tick(FPS)
    # -- Telas do jogo
    # - Tela inicial
    if state == INIT:
        state = init_screen(window)
    # - Tela primeiro chefe
    elif state == MAUA:
        state = game_screen(window, MAP, state)
    # - Tela terceiro chefe
    elif state == BOSS3:
        state = boss3_screen(window)
    elif state == WIN:
        state = win_screen(window)

pygame.quit()
