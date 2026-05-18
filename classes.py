# --- Importa e inicia pacotes
import pygame
from config import *

# Classe que representa os blocos do cenário
class Tile(pygame.sprite.Sprite):

    # Construtor da classe
    def __init__(self, tile_img, row, colum):
        # Construtor da classe pai (Sprite)
        pygame.sprite.Sprite.__init__(self)

        # Aumenta o tamanho do tile
        tile_img = pygame.transform.scale(tile_img, (TILE_SIZE, TILE_SIZE))

        # Define o próprio sprite
        self.image = tile_img
        # Detalhes sibre o posicionamento
        self.rect = self.image.get_rect()

        # Posiciona o tile
        self.rect.x = TILE_SIZE * colum
        self.rect.y = TILE_SIZE * row

# Classe que representa a protagonista
class Player(pygame.sprite.Sprite):

    # Construtor da classe
    def __init__(self, player_img, row, colum, platforms, blocks, all_bullets, assets, all_sprites):

        # Construtor da classe ppai (Sprite)
        pygame.sprite.Sprite.__init__(self)

        # Define o estado autal
        # usado para determinar as ações disponíveis para o jogador
        self.state = STILL # Começa imóvel

        # Ajusta o tamanho da imagem
        self.player_img = pygame.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
        
        # Define a imagem do sprite
        self.image = self.player_img
        # Detalhes sobre o posicionamento
        self.rect = self.image.get_rect()

        # Guarda os grupos de sprites para tratar as colisões
        self.platforms = platforms
        self.blocks = blocks

        # Posiciona o personagem
        self.rect.x = colum * TILE_SIZE
        self.rect.y = row * TILE_SIZE

        # Inicializa velocidades
        self.speedx = 0
        self.speedy = 0

        # Define altura no mapa
        # Essa variável sempre conterá a maior altura alcançada pelo jogador
        # antes de começar a cair
        self.highest_y = self.rect.bottom

        #imagem bala
        self.bulletimg = assets[BULLET1]

        #dicionário assets
        self.all_sprites = all_sprites

        #grupo balas
        self.all_bullets = all_bullets

        #tempo do tiro
        self.shoot_ticks = pygame.time.get_ticks()
        self.last_shot = 0
    
    # Método que atualiza a posição do personagem
    def update(self):
        
        # Tenta andar em y
        # Atualiza a velocidade aplicando a aceleraçao da gravidade
        self.speedy += GRAVITY
        # Atualiza o estado para "Caindo"
        if self.speedy > 0:
            self.state = FALLING

        # -- Movimento em y --
        self.rect.y += self.speedy

        # Atualiza altura no mapa
        if self.state != FALLING:
            self.highest_y = self.rect.bottom

        # Se colidiu com algum bloco, volta para o ponto antes da colisão
        collisions = pygame.sprite.spritecollide(self, self.blocks, False)
        # Corrige a posição do personagem
        for collision in collisions:
            # Se estava caindo
            if self.speedy > 0:
                # Atualiza a posição
                self.rect.bottom = collision.rect.top
                # Zera a velocidade
                self.speedy = 0
                # Atualiza o estado
                self.state = STILL
            # Se estava subindo
            elif self.speedy < 0:
                # Atualiza a posição
                self.rect.top = collision.rect.bottom
                # Zera a velocidade
                self.speedy = 0
                # Atualiza o estado
                self.state = STILL

        # Tratamento especial para plataformas
        # Plataformas devem ser transponíveis quando o personagem está pulando
        # mas devem pará-lo quando ele está caindo. Para pará-lo é necessário que
        # o jogador tenha passado daquela altura durante o último pulo.
        if self.speedy > 0: # Está indo para baixo
            collisions = pygame.sprite.spritecollide(self, self.platforms, False)
            # Para cada tile de plataforma que colidiu com o personagem
            # verifica se ele estava aproximadamente na parte de cima
            for platform in collisions:
                # Verifica se a altura alcançada durante o pulo está acima da
                # plataforma
                if self.highest_y <= platform.rect.top:
                    # Atualiza a altura
                    self.rect.bottom = platform.rect.top
                    # Zera a velocidade
                    self.speedy = 0
                    # Atualiza estado
                    self.state = STILL
            
        # -- Movimento em x --
        self.rect.x += self.speedx
        
        # Mantém a protagonista dentro da tela
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right >= WIDTH:
            self.rect.right = WIDTH - 1

        # Muda o sprite de acordo com a direção do movimento
        # Se está indo para a direita...
        if self.speedx > 0:
            # Vira para a esquerda
            self.image = pygame.transform.flip(self.player_img, False, False)
        # Caso o contrário...
        elif self.speedx < 0:
            # Vira para a esquerda
            self.image = pygame.transform.flip(self.player_img, True, False)

        # Se colidiu com algum bloco, volta para o ponto antes da colisão
        # O personagem não colide com as plataformas quando está andando na horizontal
        collisions = pygame.sprite.spritecollide(self, self.blocks, False)
        # Corrige a posição do personagem
        for collision in collisions:
            # Indo para a direita
            if self.speedx > 0:
                self.rect.right  = collision.rect.left

            # Indo para a esquerda
            elif self.speedx < 0:
                self.rect.left = collision.rect.right


    # Jogador atira
    def shoot(self):
        # Verifica se pode atirar
        now = pygame.time.get_ticks()
        # Verifica quantos ticks se passaram desde o último tiro.
        elapsed_ticks = now - self.last_shot

        # Se já pode atirar novamente...
        if elapsed_ticks > self.shoot_ticks:
            # Marca o tick da nova imagem.
            self.last_shot = now
            # A nova bala vai ser criada a partir do personagem
            new_bullet = Bullet(self.bulletimg, self.rect.x, self.rect.y)
            self.all_bullets.add(new_bullet)
            self.all_sprites.add(new_bullet)
     

    # Método que faz o personagem pular
    def jump(self):
        # Só pode pular se não estiver pulando ou caindo
        if self.state == STILL:
            self.speedy -= JUMP_SIZE
            self.state = JUMPING

class Bullet(pygame.sprite.Sprite):
    # Construtor da classe.
    def __init__(self, bullet_img, cordx, cordy):
        # Construtor da classe mãe (Sprite).
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.transform.scale(bullet_img, (20, 10))
        self.rect = self.image.get_rect()

        # Coloca no lugar inicial definido em x, y do constutor
        self.rect.center = (cordx + PLAYER_WIDTH, cordy + PLAYER_HEIGHT/2)
        self.speedx = 50  # Velocidade para o lado

    def update(self):
        # A bala só se move no eixo x
        self.rect.x += self.speedx

        # Se o tiro passar do inicio da tela, morre.
        if self.rect.x < 0 or self.rect.x > WIDTH:
            self.kill()

# Função auxiliar para determinar o movimento do jogador
def player_movement(player, event):

    # Se apertou uma tecla...
    if event.type == pygame.KEYDOWN:
        # Dependendo da tecla, altera o estado do jogador
        # - Movimento para a esquerda
        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
            player.speedx -= SPEED_X
        # - Movimento para a direita
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            player.speedx += SPEED_X
        # - Pulo
        elif event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_SPACE:
            player.jump()
        # - Tiro
        elif event.key == pygame.K_x:
            player.shoot()

    # Verifica se soltou alguma tecla.
    if event.type == pygame.KEYUP:
        # Dependendo da tecla, altera o estado do jogador.
        # - Para movimento para esquerda
        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
            player.speedx += SPEED_X
        # - Para movimento para a direita
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            player.speedx -= SPEED_X