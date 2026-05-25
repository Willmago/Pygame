# --- Importa e inicia pacotes
import pygame
from os import path
import math

# Inicializa o pygame e seus módulos
pygame.init()
pygame.mixer.init()
pygame.font.init()

# --- Constantes
# -- Tela
OG = (1080, 720)
HD = (1280, 720)
UHD = (1080, 1920)
w, h = OG
#w, h = pygame.display.get_desktop_sizes()[0] # Pega o tamanho da tela
WIDTH = w       # Largura da tela
HEIGHT = h      # Altura da tela
FPS = 30        # Taxa de quadros por segundo
TITULO = 'OI'   # Título da janela

# -- Estados de jogo
# Determinam, principalmente, a tela a ser carregada
INIT = 0    # Inicializando
MAUA = 1    # Primeiro boss
BOSS2 = 2   # Segundo boss
BOSS3 = 4   # Terceiro boss (Rato no robô)
WIN = 9     # Fim de jogo
QUIT = 10   # Jogo fecha

# -- Tamanhos
TILE_SIZE = math.ceil(WIDTH / 27)                   # Tamanho dos tiles
PLAYER_WIDTH = TILE_SIZE                # Largura do player
PLAYER_HEIGHT = int(TILE_SIZE * 1.5)    # Altura do player

# Variáveis do player
STILL = 0                   # estado No chão
JUMPING = 1                 # estado Subindo
FALLING = 2                 # estado Descendo
JUMP_SIZE = TILE_SIZE       # Força do pulo
SPEED_X = TILE_SIZE/3       # Velocidade horizontal (menor que a bala)

# - Variáveis do Mauazinho
MAUA_HP = 200                       # Vida máxima do chefe
MAUA_SPD = TILE_SIZE * (1/3)        # Velocidade de andar do chefe
MAUA_BULLET_COUNT = 5               # Número de disparos por leva
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

# -- Boss 3 (Rato no robô)
BOSS3_HP          = 300        # Vida total do boss
BOSS3_SPEED       = 4          # Velocidade de caminhada
BOSS3_WIDTH       = 200        # Largura do sprite do boss
BOSS3_HEIGHT      = 280        # Altura do sprite do boss
MINE_SIZE         = 72         # Tamanho da mina terrestre
NAIL_SPEED        = 7          # Velocidade do prego (mais lento que a bala do player)
NAIL_WIDTH        = 90         # Largura do prego
NAIL_HEIGHT       = 45         # Altura do prego
GEAR_SIZE         = 60         # Tamanho da engrenagem
EXPLOSION_SIZE    = 120        # Tamanho do sprite de explosão
EXPLOSION_DURATION = 400       # Duração da explosão em ms
GEAR_THROW_SPEED  = 10         # Velocidade horizontal da engrenagem
WRENCH_REACH      = 220        # Alcance horizontal do golpe da chave
WRENCH_TELEGRAPH  = 1200       # Tempo de aviso antes do golpe (ms)
WRENCH_ACTIVE     = 400        # Duração do hitbox ativo (ms)
ATTACK_COOLDOWN   = 2000       # Pausa entre ataques (ms)
WALK_DISTANCE     = WIDTH - BOSS3_WIDTH - 40  # Distância máxima de caminhada

# Estados do boss
BOSS_WALKING      = 'walking'
BOSS_TELEGRAPH    = 'telegraph'
BOSS_WRENCH       = 'wrench'
BOSS_NAILS        = 'nails'
BOSS_GEARS        = 'gears'
BOSS_PAUSE        = 'pause'

# --- Determina assets
# Estabelece a pasta que contem as imagens
img_dir = path.join(path.dirname(__file__), 'assets/img')
# e a que contem os sons
snd_dir = path.join(path.dirname(__file__), 'assets/snd')

# --- Imagens
# - Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PURPLE = (50, 0, 50)

# - Player
PLAYER_HP = 3
I_FRAMES = 2 * 1000         # Tempo de invulnerabilidade
PLAYER_IMG = 'player_img'   # Imagem base
BULLET1 = 'Bullet1'         # Imagem do tiro

# - Mauazinho 
MAUA_SIZE = WIDTH / 7
MAUA_BULLET_SIZE = MAUA_SIZE / 3
MAUA_IDLE_IMG = 'maua_idle'
MAUA_WALK_IMG_0 = 'maua_walk0'
MAUA_WALK_IMG_1 = 'maua_walk1'
MAUA_LASER_IMG_0 = 'maua_laser0'
MAUA_LASER_IMG_1 = 'maua_laser1'
MAUA_LASER_IMG_2 = 'maua_laser2'
MAUA_SHOOT_IMG = 'maua_shoot'
MAUA_DEAD_IMG = 'maua_dead'
MAUA_BULLET_IMG_0 = 'maua_bullet0'
MAUA_BULLET_IMG_1 = 'maua_bullet1'
MAUA_BULLET_IMG_2 = 'maua_bullet2'
LASER_IMG_0 = 'laser0'
LASER_IMG_1 =  'laser1'
MAUA_BACKGROUND_IMG = 'maua_background'

# - Cenário
LOGO_IMG = 'logo'

# -- Sons
SHOOT_SND = 'pew_snd'

# - Mauazinho
MAUA_LASER_SND = 'maua_laser_snd'
MAUA_SHOT_SND = 'maua_shot_snd'
MAUA_SHOT_SND1 = 'maua_shot_snd1'
MAUA_WALK_SND = 'maua_walk_snd'

# -- Define os tipos de tiles
BLOCK = 0
PLATF = 1
DIRTS = 2
STONE = 3
CLOUD = 4
EMPTY = -1
INVIS = 2   # Plataforma invisível (colisão sem sprite visível)

BOSS_IMG        = 'boss_img'
BOSS_WALK_IMG   = 'boss_walk_img'    # andando (perna esq frente)
BOSS_NAIL_IMG   = 'boss_nail_img'    # atirando prego
BOSS_WRENCH_IMG = 'boss_wrench_img'  # golpeando com chave
BOSS_DEAD_IMG   = 'boss_dead_img'    # derrotado
BOSS_GEAR_IMG   = 'boss_gear_img'    # jogando engrenagens
MINE_IMG        = 'mine_img'
EXPLOSION_IMG   = 'explosion_img'
NAIL_IMG        = 'nail_img'
GEAR_IMG        = 'gear_img'
WRENCH_SLASH_IMG = 'wrench_slash_img'
BG_BOSS3        = 'bg_boss3'


# - Define o mapa com os tipos de tiles (27 x 18)
MAP = [
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, CLOUD, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, CLOUD, EMPTY, EMPTY, EMPTY, CLOUD, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, CLOUD, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [CLOUD, CLOUD, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, CLOUD, CLOUD, CLOUD, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, CLOUD, CLOUD, CLOUD, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, CLOUD, CLOUD],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS, DIRTS],
    [STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE],
    [STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE],
    [STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE],
    [STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE, STONE]
]

# - Mapa do segundo boss
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

# Mapa do boss 3 — Oficina (27 colunas x 18 linhas, TILE_SIZE=40 → 1080x720)
# bg: (1080, 659), y=0
# Prateleira: linha 7,  cols 13-23 (y=280) — acima da mesa, alcançável pulando da mesa
# Mesa:       linha 11, cols 9-24  (y=440) — alcançável com pulo do chão (diff=80px)
# Chão:       linha 13 (y=520) — alinhado com chão visual
MAP3 = [
    [EMPTY]*27,  # 0
    [EMPTY]*27,  # 1
    [EMPTY]*27,  # 2
    [EMPTY]*27,  # 3
    [EMPTY]*27,  # 4
    [EMPTY]*27,  # 5
    [EMPTY]*27,  # 6
    # linha 7 — prateleira central (sobre a mesa)
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY]*27,  # 8
    [EMPTY]*27,  # 9
    [EMPTY]*27,  # 10
    # linha 11 — tampo da mesa central
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY]*27,  # 12
    # linha 13 — chão da oficina (invisível)
    [INVIS]*27,
    [EMPTY]*27,  # 14
    [EMPTY]*27,  # 15
    [EMPTY]*27,  # 16
    [EMPTY]*27,  # 17
]

# Função para carregar os assets (imagens, sons) a partir dos arquivos locais
def load_assets(img_dir):
    assets = {}
    assets[PLAYER_IMG] = pygame.image.load(path.join(img_dir, 'hero-single.png')).convert_alpha()
    assets[BLOCK]      = pygame.image.load(path.join(img_dir, 'tile-block.png')).convert()
    assets[PLATF]      = pygame.image.load(path.join(img_dir, 'tile-wood.png')).convert()
    assets[BULLET1]    = pygame.image.load(path.join(img_dir, 'Tiro1.png')).convert_alpha()

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
    assets[MAUA_BULLET_IMG_0] = pygame.image.load(path.join(img_dir, 'maua_bullet0.png')).convert_alpha()
    assets[MAUA_BULLET_IMG_1] = pygame.image.load(path.join(img_dir, 'maua_bullet1.png')).convert_alpha()
    assets[MAUA_BULLET_IMG_2] = pygame.image.load(path.join(img_dir, 'maua_bullet2.png')).convert_alpha()
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
    assets[MAUA_SHOT_SND] = pygame.mixer.Sound(path.join(snd_dir, 'maua_shot.wav'))
    assets[MAUA_SHOT_SND1] = pygame.mixer.Sound(path.join(snd_dir, 'maua_shot2.wav'))
    assets[MAUA_LASER_SND] = pygame.mixer.Sound(path.join(snd_dir, 'maua_laser.wav'))
    assets[MAUA_WALK_SND] = pygame.mixer.Sound(path.join(snd_dir, 'maua_walk.flac'))

    files = {
        BOSS_IMG:        'Chefao_Poli.png',
        BOSS_WALK_IMG:   'Sprite_lado_andando_perna_esquerda_frente.png',
        BOSS_NAIL_IMG:   'atirandoprego.png',
        BOSS_WRENCH_IMG: 'Golpeando_chave_.png',
        BOSS_DEAD_IMG:   'ratoderrotado.png',
        BOSS_GEAR_IMG:   'jogandoengrenagens.png',
        MINE_IMG:        'Mina.png',
        EXPLOSION_IMG:   'explosao.png',
        NAIL_IMG:        'Prego.png',
        GEAR_IMG:        'Engrenagem.png',
        WRENCH_SLASH_IMG: 'Golpechave.png',
        BG_BOSS3:        'Ambiente_boss3.png',
    }
    # Tamanho do placeholder por chave
    placeholder_sizes = {
        BOSS_IMG:        (BOSS3_WIDTH, BOSS3_HEIGHT),
        BOSS_WALK_IMG:   (BOSS3_WIDTH, BOSS3_HEIGHT),
        BOSS_NAIL_IMG:   (BOSS3_WIDTH, BOSS3_HEIGHT),
        BOSS_WRENCH_IMG: (BOSS3_WIDTH, BOSS3_HEIGHT),
        BOSS_DEAD_IMG:   (BOSS3_WIDTH, BOSS3_HEIGHT),
        BOSS_GEAR_IMG:   (BOSS3_WIDTH, BOSS3_HEIGHT),
        MINE_IMG:        (MINE_SIZE, MINE_SIZE),
        EXPLOSION_IMG:   (EXPLOSION_SIZE, EXPLOSION_SIZE),
        NAIL_IMG:        (NAIL_WIDTH, NAIL_HEIGHT),
        GEAR_IMG:        (GEAR_SIZE, GEAR_SIZE),
        WRENCH_SLASH_IMG: (WRENCH_REACH, WRENCH_REACH),
        BG_BOSS3:        (WIDTH, HEIGHT),
    }
    for key, filename in files.items():
        full_path = path.join(img_dir, filename)
        pw, ph = placeholder_sizes.get(key, (64, 64))
        if not path.exists(full_path):
            print(f'[BOSS3] ARQUIVO FALTANDO: {full_path}')
            surf = pygame.Surface((pw, ph))
            surf.fill((255, 0, 255))
            assets[key] = surf
        else:
            try:
                if key == BG_BOSS3:
                    assets[key] = pygame.image.load(full_path).convert()
                else:
                    assets[key] = pygame.image.load(full_path).convert_alpha()
            except Exception as e:
                print(f'[BOSS3] ERRO ao carregar {filename}: {e}')
                surf = pygame.Surface((pw, ph))
                surf.fill((255, 0, 255))
                assets[key] = surf

    return assets  

# Função para carregar e tocar uma música
def music(name, volume):
    pygame.mixer.music.load(path.join(snd_dir, name))
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()

# Gera tela principal
#window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Nome do jogo
pygame.display.set_caption(TITULO)

# Estado inicial do jogo
state = INIT        

# relógio para controle de FPS
clock = pygame.time.Clock()