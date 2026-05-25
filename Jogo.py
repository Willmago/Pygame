# --- Importa e inicia pacotes
import pygame
from config import *
from telas import init_screen, game_screen, win_screen
from boss_2 import *
from fase_boss3 import boss3_screen
from os import path

# --- Carrega imagens de vida do player
def load_hp_imgs(img_dir):
    """Carrega os sprites de HUD de vida (1, 2 e 3 vidas)."""
    hp_imgs = {}
    files = {1: '1vida.png', 2: '2vida.png', 3: '3vida.png'}
    for key, filename in files.items():
        full_path = path.join(img_dir, filename)
        if path.exists(full_path):
            hp_imgs[key] = pygame.image.load(full_path).convert_alpha()
        else:
            # Placeholder caso o arquivo não exista
            surf = pygame.Surface((200, 60))
            surf.fill((200, 50, 50) if key == 1 else (200, 200, 50) if key == 2 else (50, 200, 50))
            hp_imgs[key] = surf
    return hp_imgs
hp_imgs = load_hp_imgs(img_dir)

# --- Loop geral do jogo
music('intro.mp3', 0.2)
while state != QUIT:

    # Controle de FPS
    clock.tick(FPS)

    # -- Telas do jogo
    if state == INIT:
        state = init_screen(window)

    elif state == MAUA:
        state = game_screen(window, MAP, state, hp_imgs)
    # - Tela segundo chefe
    elif state == JARE_GV:
        state = boss_2()
    # - Tela terceiro chefe
    elif state == BOSS3:
        state = boss3_screen(window, hp_imgs)

    elif state == WIN:
        state = win_screen(window)

pygame.quit()