import pygame
from config import state, clock, window, INIT, RUNNING, QUIT, FPS
from telas import init_screen, game_screen

while state != QUIT:

    clock.tick(FPS)
    if state == INIT:
        state = init_screen(window)
    elif state == RUNNING:
        state = game_screen(window)
    

pygame.quit()