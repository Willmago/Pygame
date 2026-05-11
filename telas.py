from config import *
from classes import *

font = pygame.font.SysFont(None, 48)
init_text = font.render("Pressione qualquer tecla para iniciar", True, (10, 10, 10))
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
            state = RUNNING # ... e inicia o jogo

    window.fill((255, 0, 255))  # Preence a tela de Roxo
    window.blit(init_text, (WIDTH/2, HEIGHT/2))

    pygame.display.update()     # Atualiza a tela
    return state                # Retorna o estado para continuar o jogo

def map_init(window, mapa):
    def game_screen(window):
        clock = pygame.time.Clock()

        assets = load_assets(img_dir)

        all_sprites = pygame.sprite.Group()

        platforms = pygame.sprite.Group()

        blocks = pygame.sprite.Group()

        player = Player(assets[PLAYER_IMG], 12, 2, platforms, blocks)

        for row in range(len(mapa)):
            for colum in range(len(mapa[row])):
                tile_type = mapa[row][colum]
                if tile_type != EMPTY:
                    tile = Tile(assets[tile_type], row, colum)
                    all_sprites.add(tile)
                    if tile_type == BLOCK:
                        blocks.add(tile)
                    elif tile_type == PLATF:
                        platforms.add(tile)
            
        all_sprites.add(player)

        PLAYING = 0
        DONE = 1
        

        state = PLAYING
        while state != DONE:

            # Ajusta a velocidade do jogo.
            clock.tick(FPS)

            # Processa os eventos (mouse, teclado, botão, etc).
            for event in pygame.event.get():

                # Verifica se foi fechado.
                if event.type == pygame.QUIT:
                    state = DONE

                # Verifica se apertou alguma tecla.
                if event.type == pygame.KEYDOWN:
                    # Dependendo da tecla, altera o estado do jogador.
                    if event.key == pygame.K_LEFT:
                        player.speedx -= SPEED_X
                    elif event.key == pygame.K_RIGHT:
                        player.speedx += SPEED_X
                    elif event.key == pygame.K_UP or event.key == pygame.K_SPACE:
                        player.jump()

                # Verifica se soltou alguma tecla.
                if event.type == pygame.KEYUP:
                    # Dependendo da tecla, altera o estado do jogador.
                    if event.key == pygame.K_LEFT:
                        player.speedx += SPEED_X
                    elif event.key == pygame.K_RIGHT:
                        player.speedx -= SPEED_X

            # Depois de processar os eventos.
            # Atualiza a acao de cada sprite. O grupo chama o método update() de cada Sprite dentre dele.
            all_sprites.update()

            # A cada loop, redesenha o fundo e os sprites
            screen.fill((0, 0, 0))
            all_sprites.draw(window)

            # Depois de desenhar tudo, inverte o display.
            pygame.display.flip()

    TITULO = 'OI'
    
    # Inicialização do Pygame.
    pygame.init()
    pygame.mixer.init()

    # Tamanho da tela.
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # Nome do jogo
    pygame.display.set_caption(TITULO)

    # Imprime instruções
    print('*' * len(TITULO))
    print(TITULO.upper())
    print('*' * len(TITULO))
    print('Utilize as setas do teclado para andar e pular.')

    # Comando para evitar travamentos.
    try:
        game_screen(window)
    finally:
        pygame.quit()


def game_screen(window):

    state = RUNNING
    

    if screen == BOSS1:

        # -- Verifica os eventos do frame
        for event in pygame.event.get():
            # - Verifica se foi fechado.
            if event.type == pygame.QUIT:
                state = QUIT

        window.fill((100, 100, 100)) # Preence a tela de Roxo

    pygame.display.update()     # Atualiza a tela

    return state