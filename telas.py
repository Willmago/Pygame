# -- Importa e inicia pacotes
from config import *
from classes import *
from fase_boss3 import boss3_screen, draw_player_hp
from boss_2 import draw_boss_hp

# Garante que BOSS3 está definido mesmo que o config.py seja uma versão antiga
if 'BOSS3' not in dir():
    BOSS3 = 4

#region Textos
# Define a fonte padrão
init_font = pygame.font.SysFont('bauhaus93', 48)
dead_font = pygame.font.SysFont('georgia', 48)

# Texto da tela inicial
init_text = init_font.render("Pressione ENTER para iniciar!", True, WHITE)
init_text_rect = init_text.get_rect()    # Pega o retângulo circunscrito ao texto
text_width = init_text_rect.width        # Pega o comprimento horizontal do texto em pixels

# Texto pós morte do boss
boss_dead_txt_up = init_font.render("Mascote derrotado!", True, WHITE)
boss_text_rect_up = boss_dead_txt_up.get_rect()

boss_dead_txt_down = init_font.render("Pressione ENTER para continuar", True, WHITE)
boss_text_rect_down = boss_dead_txt_down.get_rect()

# Texto morte player
dead_txt_up = dead_font.render("Você morreu...", True, RED)
dead_txt_rect_up = dead_txt_up.get_rect()

dead_txt_down = dead_font.render("Pressione ESC para recomeçar", True, RED)
dead_txt_rect_down = dead_txt_down.get_rect()

# Texto game over
win_txt = init_font.render("Pressione ESC para sair", True, WHITE)
win_txt_rect= win_txt.get_rect()
#endregion

# Função que coloca os blocos do tileset de acordo
# com o mapa fornecido
def map_create(mapa, all_groups, assets):
    # Para cada linha...
    for row in range(len(mapa)):
        # ... e coluna:
        for colum in range(len(mapa[row])):
            # Veficia o tipo do tile
            tile_type = mapa[row][colum]
            # Checa se o tile não é vazio. Se sim, cria o tile
            # e o adiciona no grupo com todos os sprites e no
            # seu grupo específico
            if tile_type != EMPTY:
                # definição do tipo
                tile = Tile(assets[tile_type], row, colum)
                all_groups['all_sprites'].add(tile)
                
                # Bloco normal
                if tile_type == BLOCK or tile_type == DIRTS or tile_type == STONE:
                    all_groups['blocks'].add(tile)
                # Plataforma atravessável
                elif tile_type == PLATF or tile_type == CLOUD:
                    all_groups['platforms'].add(tile)

# --- Tela de início
def init_screen(window):
    
    assets = load_assets(img_dir)

    state = INIT # Define o estado como inicializando para garantir a continuidade da função

    # -- Verifica os eventos do frame
    for event in pygame.event.get():
        # - Verifica se foi fechado.
        if event.type == pygame.QUIT:
            state = QUIT

        # - Verifica se o usuário apertou alguma tecla...
        if event.type == pygame.KEYDOWN:
            # E se a tecla é "enter"...
            if event.key == pygame.K_RETURN:
                state = MAUA
            elif event.key in (pygame.K_2, pygame.K_KP2):
                state = JARE_GV
            elif event.key in (pygame.K_3, pygame.K_KP3, pygame.K_F3):
                state = BOSS3
            

    logo = assets[LOGO_IMG]
    logo_rect = logo.get_rect()
    logo = pygame.transform.scale(logo, (3*logo_rect.width/5, 3*logo_rect.width/5))
    logo_rect = logo.get_rect()
    logo_pos = (WIDTH/2 - logo_rect.width/2, HEIGHT/2 - logo_rect.height/2)

    window.fill(PURPLE)                                  # Preence a tela de Roxo
    window.blit(logo, logo_pos)
    window.blit(init_text, (WIDTH/2 - text_width/2, HEIGHT - init_text_rect.height*1.5))  # Desenha o texto no centro da tela

    pygame.display.update()     # Atualiza a tela
    return state                # Retorna o estado para continuar o jogo

# --- Tela base do jogo
def game_screen(window, mapa, boss, hp_imgs=None):

    #region -- Definições inicias
    # Relógio para FPS
    clock = pygame.time.Clock()
    # Carrega os assets
    assets = load_assets(img_dir)
    # Cria um grupo para todos os sprites
    all_sprites = pygame.sprite.Group()
    # Cria um grupo para as plataformas
    platforms = pygame.sprite.Group()
    # Cria um grupo para os blocos
    blocks = pygame.sprite.Group()
    # Cria um grupo para os tiros do player
    all_bullets = pygame.sprite.Group()
    # Cria um grupo para as ameaças,
    # tudo que é nocivo ao player
    all_enemies = pygame.sprite.Group()
    # Agrupa os grupos de sprites em
    # um dicionário
    all_groups = {
        'all_sprites': all_sprites,
        'platforms': platforms,
        'blocks': blocks,
        'all_bullets': all_bullets,
        'all_enemies': all_enemies
    }

    # Spawna o boss Mauazinho
    enemy = Mauazinho(assets, all_groups)
    # Configura a música do boss
    boss_music = 'maua_theme.mp3'
    music_vol = 0.2
    

    # Gera o player
    player = Player(assets[PLAYER_IMG], 12, 2, assets, all_groups)
    player.hp = PLAYER_HP   # garante vida cheia ao entrar na fase

    # Cria o mapa
    map_create(mapa, all_groups, assets)

    # Adiciona o boss depois para ficar acima dos tiles
    all_groups['all_enemies'].add(enemy)
    all_groups['all_sprites'].add(enemy)

    # Adiciona o player depois para garantir que vai ser
    # desenhado por cima
    all_groups['all_sprites'].add(player)
    #endregion

    # Define o estado inicial como o chefe atual
    state = boss
    # --- Loop da fase
    music(boss_music, music_vol)
    while state == boss:

        # Ajusta a velocidade do jogo.
        clock.tick(FPS)

        # Processa os eventos (mouse, teclado, botão, etc).
        for event in pygame.event.get():

            # Verifica se foi fechado.
            if event.type == pygame.QUIT:
                state = QUIT
            
            # Resolve a movimentação do jogador
            player_movement(player, event)

            # Eventos de pressionamento de tecla
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    state = JARE_GV
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    state = JARE_GV
                elif event.key == pygame.K_3:
                    state = BOSS3

                # Se o boss estiver morto e o player apertar enter...
                elif event.key == pygame.K_RETURN and enemy.alive == False:
                    # Muda de tela de acordo com o boss
                    if boss == MAUA:
                        state = JARE_GV
                # Se o player apertar "ESC" ou "R"...
                elif event.key == pygame.K_ESCAPE:
                    # Volta para a tela inicial
                    state = INIT
                    # Reseta a música
                    music('intro.mp3', 0.2)

        # Depois de processar os eventos.
        # Atualiza a acao de cada sprite. O grupo chama o método update() de cada Sprite dentre dele.
        all_sprites.update()

        # A cada loop, redesenha o fundo e os sprites
        window.fill(PURPLE)

        # Se o inimigo estiver morto...
        if enemy.alive == False:
            # Este loop faz com que os disparos do boss
            # sumam assim que ele morre
            # Para cada entidade inimiga...
            for spawn in all_enemies:
                # Se a entidade não for o próprio boss...
                if spawn != enemy:
                    # Apaga ela
                    spawn.kill()
            
            # Desenha um texto em duas linhas
            window.blit(boss_dead_txt_up, (WIDTH/2 - boss_text_rect_up.width/2, HEIGHT/4 - boss_text_rect_up.height))
            window.blit(boss_dead_txt_down, (WIDTH/2 - boss_text_rect_down.width/2, HEIGHT/4))
        
        # Se estiver vivo...
        else:
            # Desenha a barra de vida dele
            draw_boss_hp(window, enemy, 'Mauazinho')

        # Se o player estiver morto...
        if player.alive == False:
            # Desenha um texto em duas linhas
            window.blit(dead_txt_up, (WIDTH/2 - dead_txt_rect_up.width/2, HEIGHT/4 - dead_txt_rect_up.height))
            window.blit(dead_txt_down, (WIDTH/2 - dead_txt_rect_down.width/2, HEIGHT/4))
        
        # Desenha todos os sprites de acordo com a
        # ordem de criação
        all_sprites.draw(window)

        # HUD de vidas do player
        if hp_imgs:
            draw_player_hp(window, player, hp_imgs)

        # Depois de desenhar tudo, inverte o display.
        pygame.display.flip()

    return state # Retorna o estado de jogo para mudar a tela

# -- Tela de fim
def win_screen(window):

    assets = load_assets(img_dir)

    state = WIN # Define o estado como inicializando para garantir a continuidade da função

    # -- Verifica os eventos do frame
    for event in pygame.event.get():
        # - Verifica se foi fechado.
        if event.type == pygame.QUIT:
            state = QUIT

        # - Verifica se o usuário apertou alguma tecla...
        if event.type == pygame.KEYDOWN:
            # E se a tecla é "enter"...
            if event.key == pygame.K_ESCAPE:
                state = QUIT
            elif event.key == pygame.K_r:
                state = INIT

    win = assets[WIN_IMG]
    win_rect = win.get_rect()
    scale = 1
    win = pygame.transform.scale(win, (win_rect.width * scale, win_rect.width * scale))
    win_rect = win.get_rect()
    pos_x = WIDTH/2 - win_rect.width/2
    pos_y = HEIGHT/2 - 4* win_rect.height/7
    win_pos = (pos_x, pos_y)

    window.fill(PURPLE)         # Preence a tela de Roxo
    window.blit(win, win_pos)   # Desenha a imagem de fim

    # Desenha texto
    window.blit(win_txt, (WIDTH/2 - win_txt_rect.width/2, win_rect.height))

    pygame.display.update()     # Atualiza a tela
    return state                # Retorna o estado para continuar o jogo
