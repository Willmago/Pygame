# --- Importa e inicia pacotes
from config import *
from classes import *
from fase_boss3 import boss3_screen

# Garante que BOSS3 está definido mesmo que o config.py seja uma versão antiga
if 'BOSS3' not in dir():
    BOSS3 = 4

# Define a fonte padrão
init_font = pygame.font.SysFont(None, 48)

# Texto da tela inicial
init_text = init_font.render("QUALQUER COISA QUE EU ESCREVER VAI ESTAR CENTRALIZADA", True, (10, 10, 10))
text_rect = init_text.get_rect()    # Pega o retângulo circunscrito ao texto
text_width = text_rect.width        # Pega o comprimento horizontal do texto em pixels

# --- Tela de início
def init_screen(window):
    
    state = INIT # Define o estado como inicializando para garantir a continuidade da função

    # -- Verifica os eventos do frame
    for event in pygame.event.get():
        # - Verifica se foi fechado.
        if event.type == pygame.QUIT:
            state = QUIT

        # - Verifica se o usuário apertou alguma tecla...
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_3, pygame.K_KP3, pygame.K_F3):
                state = BOSS3   # Tecla 3 (ou F3, ou numpad 3) → boss do rato
            else:
                state = BOSS1   # Qualquer outra tecla → inicia o jogo normalmente

    window.fill((255, 0, 255))                                  # Preence a tela de Roxo
    window.blit(init_text, (WIDTH/2 - text_width/2, HEIGHT/2))  # Desenha o texto no centro da tela

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
    # Cria um grupo para os tiros
    all_bullets = pygame.sprite.Group()
    # Gera o player
    player = Player(assets[PLAYER_IMG], 12, 2, platforms, blocks, all_bullets, assets, all_sprites)

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
                if tile_type == BLOCK:
                    blocks.add(tile)
                # Plataforma atravessável
                elif tile_type == PLATF:
                    platforms.add(tile)
    
    # Gera o chefão e o adiciona no grupo de sprites
    mauazinho = Mauazinho(assets[MAUA_IMG], assets[MAUA_BULLET_IMG], assets[MAUA_LASER_IMG], all_sprites)
    all_sprites.add(mauazinho)

    # Adiciona o player depois para garantir que vai ser
    # desenhado por cima
    all_sprites.add(player)

    # Define o estado inicial como o chefe atual
    state = boss
    # --- Loop da fase
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

            # **Temporário**
            # Ações de debug para testar mudar de tela e resetar o jogo
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    state = BOSS2
                elif event.key == pygame.K_3:
                    state = BOSS3
                elif event.key == pygame.K_r:
                    state = INIT

            

        # Depois de processar os eventos.
        # Atualiza a acao de cada sprite. O grupo chama o método update() de cada Sprite dentre dele.
        all_sprites.update()

        # A cada loop, redesenha o fundo e os sprites
        window.fill((0, 0, 0))
        all_sprites.draw(window)

        print(mauazinho.state)

        # Depois de desenhar tudo, inverte o display.
        pygame.display.flip()

    return state # Retorna o estado de jogo para mudar a tela