# --- Importa e inicia pacotes
import pygame
from os import path

# Inicializa o pygame e seus módulos
pygame.init()
pygame.mixer.init()
pygame.font.init()

# --- Constantes
# -- Tela
WIDTH = 1080    # Largura da tela
HEIGHT = 720    # Altura da tela
FPS = 30        # Taxa de quadros por segundo
TITULO = 'OI'   # Título da janela

# -- Estados de jogo
# Determinam, principalmente, a tela a ser carregada
INIT = 0    # Inicializando
MAUA = 1   # Primeiro boss
BOSS2 = 2   # Segundo boss
QUIT = 3    # Jogo fecha

# -- Tamanhos
TILE_SIZE = WIDTH / 27                   # Tamanho dos tiles
PLAYER_WIDTH = TILE_SIZE                # Largura do player
PLAYER_HEIGHT = int(TILE_SIZE * 1.5)    # Altura do player

# - Variáveis do player
STILL = 0                   # estado No chão
JUMPING = 1                 # estado Subindo
FALLING = 2                 # estado Descendo
JUMP_SIZE = TILE_SIZE * 1.1 # Força do pulo
SPEED_X = TILE_SIZE/3       # Velocidade horizontal (menor que a bala)

# - Variáveis do Mauazinho
MAUA_HP = 100                       # Vida máxima do chefe
MAUA_SPD = TILE_SIZE * (1/3)        # Velocidade de andar do chefe
MAUA_BULLET_SPD = 10                # Velocidade horizontal das balas do chefe
MAUA_BULLET_CD = 250                # Intervalo entre as balas
MAUA_LASER_POWERUP = 2.5 * 1000     # Tempo para carregar o laser
MAUA_LASER_DURATION = 1.5 * 1000    # Duração do laser

# -- Outros
GRAVITY = 5 # Força da gravidade
 
# -- Tiro
SHOOT_COOLDOWN = 150            # Intervalo mínimo entre tiros (ms) — cadência estilo Cuphead
BULLET_SPEED = 18               # Velocidade da bala em pixels por frame
BULLET_WIDTH = TILE_SIZE        # Largura do sprite da bala
BULLET_HEIGHT = BULLET_WIDTH/2  # Altura do sprite da bala

# --- Determina assets
# Estabelece a pasta que contem as imagens
img_dir = path.join(path.dirname(__file__), 'assets/img')
# e a que contem os sons
snd_dir = path.join(path.dirname(__file__), 'assets/snd')

# --- Imagens
# - Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (50, 0, 50)

# - Player
I_FRAMES = 2 * 1000         # Tempo de invulnerabilidade
PLAYER_IMG = 'player_img'   # Imagem base
BULLET1 = 'Bullet1'         # Imagem do tiro

# - Mauazinho 
MAUA_SIZE = 128
MAUA_IDLE_IMG = 'maua_idle'
MAUA_WALK_IMG_0 = 'maua_walk0'
MAUA_WALK_IMG_1 = 'maua_walk1'
MAUA_LASER_IMG_0 = 'maua_laser0'
MAUA_LASER_IMG_1 = 'maua_laser1'
MAUA_LASER_IMG_2 = 'maua_laser2'
MAUA_SHOOT_IMG = 'maua_shoot'
MAUA_DEAD_IMG = 'maua_dead'
MAUA_BULLET_IMG = BULLET1
LASER_IMG_0 = 'laser0'
LASER_IMG_1 =  'laser1'
MAUA_BACKGROUND_IMG = 'maua_background'

# - Cenário
LOGO_IMG = 'logo'

# -- Sons
SHOOT_SND = 'pew_snd'

# - Define os tipos de tiles
BLOCK = 0
PLATF = 1
DIRTS = 2
STONE = 3
CLOUD = 4
EMPTY = -1

# Define o mapa com os tipos de tiles (27 x 18)
MAP = [
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, CLOUD, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, CLOUD, EMPTY, EMPTY, EMPTY, CLOUD, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, CLOUD, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [CLOUD, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, CLOUD, CLOUD, CLOUD, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, CLOUD, CLOUD, CLOUD, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, CLOUD],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS],
    [STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE],
    [STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE],
    [STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE],
    [STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE]
]

# Mapa do segundo boss
MAP2 = [
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [BLOCK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [BLOCK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [BLOCK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [BLOCK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [BLOCK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [BLOCK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [BLOCK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [BLOCK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [BLOCK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK]
]

# Função para carregar os assets (imagens, sons) a partir dos arquivos locais
def load_assets(img_dir):
    assets = {}
    assets[PLAYER_IMG] = pygame.image.load(path.join(img_dir, 'hero-single.png')).convert_alpha()
    assets[BULLET1] = pygame.image.load(path.join(img_dir, 'Tiro1.png')).convert_alpha()

    # Mauazinho
    assets[MAUA_IDLE_IMG] = pygame.image.load(path.join(img_dir, 'maua_idle.png')).convert_alpha()
    assets[MAUA_WALK_IMG_0] = pygame.image.load(path.join(img_dir, 'maua_walk0.png')).convert_alpha()
    assets[MAUA_WALK_IMG_1] = pygame.image.load(path.join(img_dir, 'maua_walk1.png')).convert_alpha()
    assets[MAUA_LASER_IMG_0] = pygame.image.load(path.join(img_dir, 'maua_laser0.png')).convert_alpha()
    assets[MAUA_LASER_IMG_1] = pygame.image.load(path.join(img_dir, 'maua_laser1.png')).convert_alpha()
    assets[MAUA_LASER_IMG_2] = pygame.image.load(path.join(img_dir, 'maua_laser2.png')).convert_alpha()
    assets[MAUA_SHOOT_IMG] = pygame.image.load(path.join(img_dir, 'maua_shoot.png')).convert_alpha()
    assets[MAUA_DEAD_IMG] = pygame.image.load(path.join(img_dir, 'maua_dead.png')).convert_alpha()
    assets[LASER_IMG_0] = pygame.image.load(path.join(img_dir, 'laser0.png')).convert_alpha()
    assets[LASER_IMG_1] = pygame.image.load(path.join(img_dir, 'laser1.png')).convert_alpha()
    assets[MAUA_BACKGROUND_IMG] = pygame.image.load(path.join(img_dir, 'maua_background.png')).convert()

    # - Cenário
    assets[LOGO_IMG] = pygame.image.load(path.join(img_dir, 'logo.png')).convert_alpha()
    assets[BLOCK] = pygame.image.load(path.join(img_dir, 'tile-block.png')).convert()
    assets[PLATF] = pygame.image.load(path.join(img_dir, 'tile-wood.png')).convert()
    assets[DIRTS] = pygame.image.load(path.join(img_dir, 'dirt.png')).convert_alpha()
    assets[STONE] = pygame.image.load(path.join(img_dir, 'stone.png')).convert_alpha()
    assets[CLOUD] = pygame.image.load(path.join(img_dir, 'cloud.png')).convert_alpha()

    # - Sons
    assets[SHOOT_SND] = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))

    return assets

# Gera tela principal
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Nome do jogo
pygame.display.set_caption(TITULO)

# Estado inicial do jogo
state = INIT        

# relógio para controle de FPS
clock = pygame.time.Clock()