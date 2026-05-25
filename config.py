# --- Importa e inicia pacotes
import pygame
from os import path

# Inicializa o pygame
pygame.init()
pygame.mixer.init()

# --- Constantes
# -- Tela
WIDTH = 1080    # Largura da tela
HEIGHT = 720    # Altura da tela
FPS = 30        # Taxa de quadros por segundo
TITULO = 'OI'   # Título da janela

# -- Estados de jogo
# Determinam, principalmente, a tela a ser carregada
INIT = 0    # Inicializando
BOSS1 = 1   # Primeiro boss
BOSS2 = 2   # Segundo boss
QUIT = 3    # Jogo fecha
BOSS3 = 4   # Terceiro boss (Rato no robô)

# -- Tamanhos
TILE_SIZE = 40                          # Tamanho dos tiles
PLAYER_WIDTH = TILE_SIZE                # Largura do player
PLAYER_HEIGHT = int(TILE_SIZE * 1.5)    # Altura do player

# Variáveis do player
STILL = 0                   # estado No chão
JUMPING = 1                 # estado Subindo
FALLING = 2                 # estado Descendo
JUMP_SIZE = TILE_SIZE * 1.2 # Força do pulo
SPEED_X = 6                 # Velocidade horizontal (menor que a bala)

# -- Outros
GRAVITY = 5 # Força da gravidade

# -- Tiro
SHOOT_COOLDOWN = 150  # Intervalo mínimo entre tiros (ms) — cadência estilo Cuphead
BULLET_SPEED = 18     # Velocidade da bala em pixels por frame
BULLET_WIDTH = 40     # Largura do sprite da bala
BULLET_HEIGHT = 20    # Altura do sprite da bala

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

# Imagens
PLAYER_IMG      = 'player_img'
BULLET1         = 'Bullet1'
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

# Imagens do Boss 1 (Mauazinho)
MAUA_IMG        = 'maua_img'
MAUA_BULLET_IMG = 'maua_bullet_img'
MAUA_LASER_IMG  = 'maua_laser_img'

# -- Boss 1 (Mauazinho)
MAUA_SPD        = 4    # Velocidade de caminhada do Mauazinho
MAUA_BULLET_SPD = 8    # Velocidade da bala do Mauazinho
MAUA_BULLET_CD  = 800  # Cooldown entre tiros do Mauazinho (ms)

# Define os tipos de tiles
BLOCK = 0
PLATF = 1
EMPTY = -1
INVIS = 2   # Plataforma invisível (colisão sem sprite visível)

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
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PLATF, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PLATF, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PLATF, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PLATF, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PLATF, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PLATF, BLOCK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PLATF, EMPTY, BLOCK, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK, BLOCK]
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

    # Assets do Boss 1 (Mauazinho)
    maua_files = {
        MAUA_IMG:        'mauazinho.png',
        MAUA_BULLET_IMG: 'maua_bullet.png',
        MAUA_LASER_IMG:  'maua_laser.png',
    }
    for key, filename in maua_files.items():
        full_path = path.join(img_dir, filename)
        if not path.exists(full_path):
            print(f'[BOSS1] ARQUIVO FALTANDO: {full_path}')
            surf = pygame.Surface((64, 64))
            surf.fill((255, 0, 255))
            assets[key] = surf
        else:
            try:
                assets[key] = pygame.image.load(full_path).convert_alpha()
            except Exception as e:
                print(f'[BOSS1] ERRO ao carregar {filename}: {e}')
                surf = pygame.Surface((64, 64))
                surf.fill((255, 0, 255))
                assets[key] = surf

    return assets


# Função separada para carregar os assets exclusivos do boss3
# Chamada apenas quando a fase do boss3 é iniciada
def load_boss3_assets(img_dir):
    assets = load_assets(img_dir)  # reutiliza os assets base
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

# Gera tela principal
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Nome do jogo
pygame.display.set_caption(TITULO)

# Estado inicial do jogo
state = INIT        

# relógio para controle de FPS
clock = pygame.time.Clock()