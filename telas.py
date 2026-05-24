# --- Importa e inicia pacotes
from config import *
from classes import *


# Define a fonte padrão
init_font = pygame.font.SysFont('bauhaus93', 48)

# Texto da tela inicial
init_text = init_font.render("Pressione ENTER para iniciar!", True, WHITE)
init_text_rect = init_text.get_rect()    # Pega o retângulo circunscrito ao texto
text_width = init_text_rect.width        # Pega o comprimento horizontal do texto em pixels

# Texto pós morte do boss
boss_dead_txt_up = init_font.render("Mascote derrotado!", True, WHITE)
boss_text_rect_up = boss_dead_txt_up.get_rect()

boss_dead_txt_down = init_font.render("Pressione ENTER para continuar", True, WHITE)
boss_text_rect_down = boss_dead_txt_down.get_rect()



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
                state = MAUA # ... e inicia o jogo

    logo = assets[LOGO_IMG]
    logo_rect = logo.get_rect()
    logo = pygame.transform.scale(logo, (logo_rect.width/2, logo_rect.width/2))
    logo_rect = logo.get_rect()
    logo_pos = (WIDTH/2 - logo_rect.width/2, HEIGHT/2 - logo_rect.height/2)

    window.fill(PURPLE)                                  # Preence a tela de Roxo
    window.blit(logo, logo_pos)
    window.blit(init_text, (WIDTH/2 - text_width/2, 4*HEIGHT/5))  # Desenha o texto no centro da tela

    pygame.display.update()     # Atualiza a tela
    return state                # Retorna o estado para continuar o jogo

# --- Tela base do jogo
def game_screen(window, mapa, boss):

    # -- Definições inicias
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

    # Gera o chefão de acordo com a tela
    if boss == MAUA:
        # Spawna o boss Mauazinho
        enemy = Mauazinho(assets, all_groups)
        # Configura a música do boss
        pygame.mixer.music.load(path.join(snd_dir, 'maua_theme.mp3'))
        pygame.mixer.music.set_volume(0.4)
    elif boss == BOSS2:
        enemy = Player(assets[PLAYER_IMG], 12, 2, assets, all_groups)

    # Gera o player
    player = Player(assets[PLAYER_IMG], 12, 2, assets, all_groups)

    # -- Cria o mapa de acordo com a variável fornecida
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
                all_sprites.add(tile)
                
                # Bloco normal
                if tile_type == BLOCK or tile_type == DIRTS or tile_type == STONE:
                    blocks.add(tile)
                # Plataforma atravessável
                elif tile_type == PLATF or tile_type == CLOUD:
                    platforms.add(tile)

    # Adiciona o boss depois para ficar acima dos tiles
    all_groups['all_enemies'].add(enemy)
    all_groups['all_sprites'].add(enemy)

    # Adiciona o player depois para garantir que vai ser
    # desenhado por cima
    all_groups['all_sprites'].add(player)

    # Define o estado inicial como o chefe atual
    state = boss
    # --- Loop da fase
    pygame.mixer.music.play(loops=-1)
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
                # Se o boss estiver morto e o player apertar enter...
                if event.key == pygame.K_RETURN and enemy.alive == False:
                    # Muda de tela de acordo com o boss
                    if boss == MAUA:
                        state = BOSS2
                # Se o player apertar "ESC"...
                elif event.key == pygame.K_ESCAPE:
                    # Volta para a tela inicial
                    state = INIT
        
        # Este loop faz com que os disparos do boss
        # sumam assim que ele morre
        # Se o boss estiver morto...
        if enemy.alive == False:
            # Para cada entidade inimiga...
            for spawn in all_enemies:
                # Se a entidade não for o próprio boss...
                if spawn != enemy:
                    # Apaga ela
                    spawn.kill()

        # Depois de processar os eventos.
        # Atualiza a acao de cada sprite. O grupo chama o método update() de cada Sprite dentre dele.
        all_sprites.update()

        # A cada loop, redesenha o fundo e os sprites
        window.fill(PURPLE)

        all_sprites.draw(window)
        
        # Se o inimigo estiver morto...
        if enemy.alive == False:
            # Desenha um texto em duas linhas
            window.blit(boss_dead_txt_up, (WIDTH/2 - boss_text_rect_up.width/2, HEIGHT/4 - boss_text_rect_up.height))
            window.blit(boss_dead_txt_down, (WIDTH/2 - boss_text_rect_down.width/2, HEIGHT/4))

        # Depois de desenhar tudo, inverte o display.
        pygame.display.flip()

    return state # Retorna o estado de jogo para mudar a tela