# --- Importa e inicia pacotes
import pygame

pygame.init()

# --- Constantes
# -- Tela
WIDTH = 1080
HEIGHT = 720
FPS = 30

# -- Estados de jogo
INIT = 0
RUNNING = 1
QUIT = 2

# --- Gera tela principal
window = pygame.display.set_mode((WIDTH, HEIGHT))

#
state = INIT

clock = pygame.time.Clock()