# --- Importa e inicia pacotes
import pygame
from config import *
from telas import init_screen, game_screen
from fase_boss3 import boss3_screen

# --- Loop geral do jogo
while state != QUIT:

    # Controle de FPS
    clock.tick(FPS)
    # -- Telas do jogo
    # - Tela inicial
    if state == INIT:
        state = init_screen(window)
    # - Tela primeiro chefe
    elif state == BOSS1:
        state = game_screen(window, MAP, state)
    # - Tela segundo chefe
    elif state == BOSS2:
        state = game_screen(window, MAP2, state)
    # - Tela terceiro chefe
    elif state == BOSS3:
        state = boss3_screen(window)

pygame.quit()
