from config import *

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

def game_screen(window):

    state = RUNNING

    # -- Verifica os eventos do frame
    for event in pygame.event.get():
        # - Verifica se foi fechado.
        if event.type == pygame.QUIT:
            state = QUIT

    window.fill((100, 100, 100))# Preence a tela de Roxo

    pygame.display.update()     # Atualiza a tela

    return state