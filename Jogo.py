# --- Importa e inicia pacotes
import pygame
from config import *
from telas import init_screen, game_screen

# --- Loop geral do jogo
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
    # - Tela segundo chefe
    elif state == BOSS2:
        state = game_screen(window, MAP2, state)

pygame.quit()
