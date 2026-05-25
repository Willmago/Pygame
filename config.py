# --- Importa e inicia pacotes
import pygame, random, math, json, base64, io
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
JARE_GV = 2   # Segundo boss
BOSS3 = 4   # Terceiro boss (Rato no robô)
WIN = 9     # Fim de jogo
QUIT = 10   # Jogo fecha

#region Variáveis gerais
# -- Tamanhos
TILE_SIZE = math.ceil(WIDTH / 27)                   # Tamanho dos tiles
PLAYER_WIDTH = TILE_SIZE * 2                # Largura do player
PLAYER_HEIGHT = (TILE_SIZE * 2)    # Altura do player

# Variáveis do player
PLAYER_HP = 3
I_FRAMES = 2 * 1000         # Tempo de invulnerabilidade    
STILL = 0                   # estado No chão
JUMPING = 1                 # estado Subindo
FALLING = 2                 # estado Descendo
JUMP_SIZE = TILE_SIZE       # Força do pulo
JUMP_SIZE_BOSS3 = int(TILE_SIZE * 1.35)  # Pulo um pouco mais alto no boss 3
SPEED_X = TILE_SIZE/3       # Velocidade horizontal (menor que a bala)

# - Variáveis do Mauazinho
MAUA_HP = 200                       # Vida máxima do chefe
MAUA_SPD = TILE_SIZE * (1/4)        # Velocidade de andar do chefe
MAUA_BULLET_COUNT = 5               # Número de disparos por leva
MAUA_BULLET_SPD = 10                # Velocidade horizontal das balas do chefe
MAUA_BULLET_CD = 0.5 * 1000           # Intervalo entre as balas
MAUA_LASER_POWERUP = 2.5 * 1000     # Tempo para carregar o laser
MAUA_LASER_DURATION = 1.5 * 1000    # Duração do laser

# -- Outros
GRAVITY = 5 # Força da gravidade

# -- Tiro
SHOOT_COOLDOWN = 150            # Intervalo mínimo entre tiros (ms) — cadência estilo Cuphead
BULLET_SPEED = 18               # Velocidade da bala em pixels por frame
BULLET_WIDTH = TILE_SIZE*2        # Largura do sprite da bala
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
#endregion

#region assets
# --- Determina assets
# Estabelece a pasta que contem as imagens
img_dir = path.join(path.dirname(__file__), 'assets/img')
# e a que contem os sons
snd_dir = path.join(path.dirname(__file__), 'assets/snd')

# Imagens do Boss 1 (Mauazinho)
MAUA_IMG        = 'maua_img'
MAUA_BULLET_IMG = 'maua_bullet_img'
MAUA_LASER_IMG  = 'maua_laser_img'

# --- Imagens
# - Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PURPLE = (50, 0, 50)

# - Player
PLAYER_IMG = 'player_img'   # Imagem base
JUMP_IMG = 'jump_img'
BULLET1 = 'bullet_img'         # Imagem do tiro

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
WIN_IMG = 'win'

# -- Sons
SHOOT_SND = 'pew_snd'

# - Mauazinho
MAUA_LASER_SND = 'maua_laser_snd'
MAUA_SHOT_SND = 'maua_shot_snd'
MAUA_SHOT_SND1 = 'maua_shot_snd1'
MAUA_WALK_SND = 'maua_walk_snd'

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
#endregion

# -- Define os tipos de tiles
BLOCK = 0
PLATF = 1
DIRTS = 2
STONE = 3
CLOUD = 4
EMPTY = -1
INVIS = 2   # Plataforma invisível (colisão sem sprite visível)

# - Define o mapa com os tipos de tiles (27 x 18)
MAP = [
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, CLOUD, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, CLOUD, EMPTY, EMPTY, EMPTY],
    [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, CLOUD, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
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
# Mapa do boss 3 — Oficina (27 colunas x 18 linhas, TILE_SIZE=40 → 1080x720)
# bg: (1080, 659), y=0
# Prateleira esq: linha 6, cols 2-6   | Prateleira central: linha 6, cols 13-18
# Armários esq:   linha 10, cols 2-7  | Bancada central:    linha 10, cols 9-19
# Chão:           linha 13 (y=520)
MAP3 = [
    [EMPTY]*27,  # 0
    [EMPTY]*27,  # 1
    [EMPTY]*27,  # 2
    [EMPTY]*27,  # 3
    [EMPTY]*27,  # 4
    [EMPTY]*27,  # 5
    # linha 6 — prateleira esquerda (cols 2-6) + prateleira central (cols 13-18)
    [EMPTY, EMPTY, INVIS, INVIS, INVIS, INVIS, INVIS, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY]*27,  # 7
    [EMPTY]*27,  # 8
    [EMPTY]*27,  # 9
    # linha 10 — armários esquerda (cols 2-7) + bancada central (cols 9-19)
    [EMPTY, EMPTY, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, EMPTY, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, INVIS, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
    [EMPTY]*27,  # 11
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
    #region Player
    assets[PLAYER_IMG] = pygame.image.load(path.join(img_dir, 'raposa_arminha.png')).convert_alpha()
    assets[JUMP_IMG] = pygame.image.load(path.join(img_dir, 'raposa_pulando.png')).convert_alpha()
    assets[BULLET1]    = pygame.image.load(path.join(img_dir, 'tiro.png')).convert_alpha()
    #endregion
    #region Mauazinho
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
    #endregion
    #region - Cenário
    assets[LOGO_IMG] = pygame.image.load(path.join(img_dir, 'logo.png')).convert_alpha()
    assets[WIN_IMG] = pygame.image.load(path.join(img_dir, 'ultimate_fox.png')).convert_alpha()
    assets[BLOCK] = pygame.image.load(path.join(img_dir, 'tile-block.png')).convert()
    assets[PLATF] = pygame.image.load(path.join(img_dir, 'tile-wood.png')).convert()
    assets[DIRTS] = pygame.image.load(path.join(img_dir, 'dirt.png')).convert_alpha()
    assets[STONE] = pygame.image.load(path.join(img_dir, 'stone.png')).convert_alpha()
    assets[CLOUD] = pygame.image.load(path.join(img_dir, 'cloud.png')).convert_alpha()
    #endregion
    #region - Sons
    assets[SHOOT_SND] = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
    assets[MAUA_SHOT_SND] = pygame.mixer.Sound(path.join(snd_dir, 'maua_shot.wav'))
    assets[MAUA_SHOT_SND1] = pygame.mixer.Sound(path.join(snd_dir, 'maua_shot2.wav'))
    assets[MAUA_LASER_SND] = pygame.mixer.Sound(path.join(snd_dir, 'maua_laser.wav'))
    assets[MAUA_WALK_SND] = pygame.mixer.Sound(path.join(snd_dir, 'maua_walk.flac'))
    #endregion
    #region Rato Poli
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
    #endregion
    return assets  

# Função para carregar e tocar uma música
def music(name, volume):
    pygame.mixer.music.load(path.join(snd_dir, name))
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)

# Gera tela principal
#window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Nome do jogo
pygame.display.set_caption(TITULO)

# Estado inicial do jogo
state = INIT        

# relógio para controle de FPS
clock = pygame.time.Clock()

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

#region jaré da GV
font_large = pygame.font.SysFont("Arial", 64, bold=True)
font_med   = pygame.font.SysFont("Arial", 36, bold=True)
font_small = pygame.font.SysFont("Arial", 24)

# ===== Paleta =====
C_BLACK     = (10,  10,  10)
C_WHITE     = (255, 255, 255)
C_RED       = (220, 50,  50)
C_YELLOW    = (255, 220, 0)
C_DARK_GRAY = (60,  60,  60)
C_GREEN     = (40,  180, 80)
C_OUTLINE   = (10,  10,  10)

# ===== Constantes =====
# Chão de pedra alinhado com o piso da imagem de fundo (y≈596 na tela 720p)
GROUND_Y      = 596
PLAYER_SPEED  = 5
PLAYER_JUMP_V = -16
GRAVITY_2     = 0.7
PLAYER_W      = 52
PLAYER_H      = 68
BOSS_HP_MAX   = 135
PLAYER_HP_MAX = 3
PLAYER_W      = 52
PLAYER_H      = 68

FALL_SPD_MIN = 3.0
FALL_SPD_MAX = 5.0
HORIZ_SPD    = 5.0
DIAG_SPD     = 3.5
MIN_GAP      = PLAYER_W + 40   # 92 px corredor livre

PHASE2_HP = BOSS_HP_MAX * 2 / 3   # 90
PHASE3_HP = BOSS_HP_MAX * 1 / 3   # 45

# ===== Carrega sprites =====
def load_pixil(path):
    import PIL.Image
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    src = data["frames"][0]["layers"][0]["src"]
    b64 = src.split(",", 1)[1]
    buf = io.BytesIO(base64.b64decode(b64))
    img = PIL.Image.open(buf).convert("RGBA")
    bbox = img.getbbox()
    if bbox: img = img.crop(bbox)
    return pygame.image.frombytes(img.tobytes(), img.size, "RGBA").convert_alpha()

_boss_raw       = load_pixil("assets/img/jacare.pixil")
_missil_raw     = load_pixil("assets/img/míssil.pixil")
_cauda_raw       = load_pixil("assets/img/cauda.pixil")
_perigo_raw      = load_pixil("assets/img/perigo.pixil")
_bolinha_raw     = load_pixil("assets/img/bolinha.pixil")
_raposa_raw      = load_pixil("assets/img/raposaarminha.pixil")
_raposa_pulo_raw = load_pixil("assets/img/raposapulando.pixil")
_tiro_raw        = load_pixil("assets/img/tiro.pixil")

# Boss 3x
boss_sprite = pygame.transform.scale(_boss_raw,
    (_boss_raw.get_width()*3, _boss_raw.get_height()*3))
BOSS_W = boss_sprite.get_width()
BOSS_H = boss_sprite.get_height()

# Imagem de fundo
bg_image = pygame.transform.scale(
    pygame.image.load("assets/img/fortalezajacare.png").convert(), (WIDTH, HEIGHT))

# Rostos boss 3x
_face_raws = [load_pixil("assets/img/rosto_jacare1.pixil"),
            load_pixil("assets/img/rosto_jacare_3.pixil"),
            load_pixil("assets/img/rosto_jacare_4.pixil")]
boss_faces = [pygame.transform.scale(r, (r.get_width()*3, r.get_height()*3))
            for r in _face_raws]

# Míssil vertical fino 19x76
_mf2 = pygame.transform.scale(_missil_raw,
    (_missil_raw.get_width()*2, _missil_raw.get_height()*2))
missil_fall = pygame.transform.scale(_mf2, (19, 76))
BULLET_W, BULLET_H = missil_fall.get_width(), missil_fall.get_height()

# Míssil horizontal
_mh2 = pygame.transform.scale(_missil_raw,
    (_missil_raw.get_width()*2, _missil_raw.get_height()*2))
missil_horiz = pygame.transform.rotate(_mh2, -90)
HORIZ_W, HORIZ_H = missil_horiz.get_width(), missil_horiz.get_height()

# Mísseis diagonais
missil_diag_r = pygame.transform.rotate(missil_fall,  45)
missil_diag_l = pygame.transform.rotate(missil_fall, -45)

# Cauda fase 1 — rotacionada 90° e flipada → ponta embaixo, escala 5x
JACARE_ZONE = WIDTH // 3
_cauda_rot  = pygame.transform.flip(pygame.transform.rotate(_cauda_raw, 90), False, True)
JLADO_W     = _cauda_rot.get_width()  * 5
JLADO_H     = _cauda_rot.get_height() * 5
jacarelado_sprite = pygame.transform.scale(_cauda_rot, (JLADO_W, JLADO_H))

# Sinal de perigo fase 1
PERIGO_W = JACARE_ZONE
PERIGO_H = int(_perigo_raw.get_height() * (JACARE_ZONE / _perigo_raw.get_width()))
perigo_sprite = pygame.transform.scale(_perigo_raw, (PERIGO_W, PERIGO_H))

# Bolinha fase 3 — 2x
bolinha_sprite = pygame.transform.scale(_bolinha_raw,
    (_bolinha_raw.get_width()*2, _bolinha_raw.get_height()*2))
BOLINHA_W = bolinha_sprite.get_width()
BOLINHA_H = bolinha_sprite.get_height()

# Raposa — sprite original olha para a ESQUERDA
# facing=-1 → sprite normal  |  facing=1 → flip horizontal
raposa_sprite      = pygame.transform.scale(_raposa_raw,     (52, 68))
raposa_sprite_flip = pygame.transform.flip(raposa_sprite,     True, False)
raposa_pulo        = pygame.transform.scale(_raposa_pulo_raw, (52, 68))
raposa_pulo_flip   = pygame.transform.flip(raposa_pulo,       True, False)

# Tiro — 16x8
tiro_sprite      = pygame.transform.scale(_tiro_raw, (16, 8))
tiro_sprite_flip = pygame.transform.flip(tiro_sprite, True, False)
PBULLET_W = 16
PBULLET_H = 8

# Plataforma do boss
# Boss posicionado em cima da placa "Ordem Disciplina Resultados"
# Placa: x=820..1080, topo em y≈480 na tela 720p
SIGN_TOP_Y = 480    # topo da placa no jogo
SIGN_CX    = 950    # centro X da placa (820 + 260/2)
BOSS_X     = SIGN_CX - BOSS_W // 2   # centralizado sobre a placa
BOSS_Y     = SIGN_TOP_Y - BOSS_H     # pés do boss exatamente no topo da placa

# Platform virtual (sem desenho) — usado para limitar área de projéteis
PLATFORM_X = 820
PLATFORM_W = 260
PLATFORM_Y = SIGN_TOP_Y

# Altura rasteira para mísseis fase 3 (próximo ao chão)
P3_HORIZ_Y_MIN = GROUND_Y - HORIZ_H - 10
P3_HORIZ_Y_MAX = GROUND_Y - HORIZ_H - 2
#endregion