import pygame
from config import *
from telas import init_screen, game_screen


while state != QUIT:

    clock.tick(FPS)
    if state == INIT:
        state = init_screen(window)
    elif state == BOSS1:
        state = game_screen(window, MAP, state)
    elif state == BOSS2:
        state = game_screen(window, MAP2, state)

pygame.quit()
