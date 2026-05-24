# --- Importa e inicia pacotes
import pygame
import math
from config import *
import random

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
    def __init__(self, player_img, row, colum, assets, all_groups):

        # Construtor da classe ppai (Sprite)
        pygame.sprite.Sprite.__init__(self)

        # Define o estado autal
        # usado para determinar as ações disponíveis para o jogador
        self.state = STILL # Começa imóvel

        # Vida inicial
        self.hp = 5

        # Ajusta o tamanho da imagem
        self.player_img = pygame.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.img_flipped = pygame.transform.flip(self.player_img, True, False)

        # Define a imagem do sprite
        self.image = self.player_img
        # Detalhes sobre o posicionamento
        self.rect = self.image.get_rect()

        # Guarda os grupos de sprites para tratar as colisões
        self.platforms = all_groups['platforms']
        self.blocks = all_groups['blocks']

        # Posiciona o personagem
        self.rect.x = colum * TILE_SIZE
        self.rect.y = row * TILE_SIZE

        # Inicializa velocidades
        self.speedx = 0
        self.speedy = 0

        # Direção que o jogador está virado (1 = direita, -1 = esquerda)
        # Ainda usado para espelhar o sprite
        self.direction = 1

        # Define altura no mapa
        # Essa variável sempre conterá a maior altura alcançada pelo jogador
        # antes de começar a cair
        self.highest_y = self.rect.bottom

        #imagem bala
        self.bulletimg = assets[BULLET1]

        #dicionário assets
        self.all_sprites = all_groups['all_sprites']

        #grupo balas
        self.all_bullets = all_groups['all_bullets']

        #grupo inimigos
        self.all_enemies = all_groups['all_enemies']

        # Marca o tempo do último tiro (em ms)
        self.last_shot = 0
    
    # Método que atualiza a posição do personagem
    def update(self):

        # Dispara enquanto o botão esquerdo do mouse estiver pressionado
        if pygame.mouse.get_pressed()[0]:
            self.shoot()
        
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

        # Vira o sprite conforme a posição do cursor, não do movimento
        mouse_x, _ = pygame.mouse.get_pos()
        if mouse_x >= self.rect.centerx:
            # Cursor à direita — sprite normal
            self.image = pygame.transform.flip(self.player_img, False, False)
            self.direction = 1
        else:
            # Cursor à esquerda — sprite espelhado
            self.image = pygame.transform.flip(self.player_img, True, False)
            self.direction = -1

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

        hits = pygame.sprite.spritecollide(self, self.all_enemies, False)

        for hit in hits:
            self.hp -= 1
        
        if self.hp <= 0:
            self.dead()
    # Jogador atira em direção ao cursor do mouse
    def shoot(self):
        # Verifica se pode atirar
        now = pygame.time.get_ticks()
        elapsed = now - self.last_shot

        # Se já pode atirar novamente...
        if elapsed > SHOOT_COOLDOWN:
            self.last_shot = now
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Origem do tiro: frente do personagem conforme a direção que ele está virado
            if self.direction == 1:
                # Virado para direita: tiro sai da borda direita, meio vertical
                origin_x = self.rect.right
            else:
                # Virado para esquerda: tiro sai da borda esquerda, meio vertical
                origin_x = self.rect.left
            origin_y = self.rect.centery

            new_bullet = Bullet(
                self.bulletimg,
                origin_x, origin_y,
                mouse_x, mouse_y,
                self.blocks, self.platforms
            )
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
    # origin_x, origin_y: ponto de saída do tiro (já calculado pelo Player)
    # target_x, target_y: posição do cursor (alvo)
    # blocks: grupo de blocos sólidos do mapa para colisão
    def __init__(self, bullet_img, origin_x, origin_y, target_x, target_y, blocks, platforms):
        pygame.sprite.Sprite.__init__(self)

        # Guarda apenas os blocos sólidos para colisão (plataformas são atravessáveis)
        self.blocks = blocks

        # Calcula o vetor normalizado em direção ao cursor
        dx = target_x - origin_x
        dy = target_y - origin_y
        distancia = max(1, (dx**2 + dy**2) ** 0.5)
        self.vx = (dx / distancia) * BULLET_SPEED
        self.vy = (dy / distancia) * BULLET_SPEED

        # Rotaciona a imagem para apontar na direção certa
        angulo = -math.degrees(math.atan2(dy, dx))
        bullet_img_scaled = pygame.transform.scale(bullet_img, (BULLET_WIDTH, BULLET_HEIGHT))
        self.image = pygame.transform.rotate(bullet_img_scaled, angulo).convert_alpha()
        self.rect = self.image.get_rect(center=(origin_x, origin_y))

        # Posição em float para movimento suave e preciso
        self.pos_x = float(origin_x)
        self.pos_y = float(origin_y)

    def update(self):
        # Move a bala
        self.pos_x += self.vx
        self.pos_y += self.vy
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

        # Destrói ao sair da tela
        if self.rect.x < 0 or self.rect.x > WIDTH or self.rect.y < 0 or self.rect.y > HEIGHT:
            self.kill()
            return

        # Destrói ao colidir com blocos sólidos do mapa
        # (plataformas atravessáveis não bloqueiam o tiro)
        if pygame.sprite.spritecollide(self, self.blocks, False):
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

    # Verifica se soltou alguma tecla.
    if event.type == pygame.KEYUP:
        # Dependendo da tecla, altera o estado do jogador.
        # - Para movimento para esquerda
        if event.key == pygame.K_LEFT or event.key == pygame.K_a:
            player.speedx += SPEED_X
        # - Para movimento para a direita
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            player.speedx -= SPEED_X

class Mauazinho(pygame.sprite.Sprite):
    def __init__(self, assets, all_groups):
        # Construtor da classe pai (Sprite)
        pygame.sprite.Sprite.__init__(self)

        # Salva o grupo de sprites como um atributo
        self.all_sprites = all_groups['all_sprites']
        self.all_enemies = all_groups['all_enemies']
        self.all_bullets = all_groups['all_bullets']

        # Tamanho base
        size = (MAUA_SIZE, MAUA_SIZE)

        # -- Definição das imagens
        # Imagem normal
        self.idle_img = pygame.transform.scale(assets[MAUA_IDLE_IMG], size)
        # Andando
        self.walk_img0 = pygame.transform.scale(assets[MAUA_WALK_IMG_0], size)
        self.walk_img1 = pygame.transform.scale(assets[MAUA_WALK_IMG_1], size)
        self.walk_fps = 300
        # Atirando
        self.shoot_img = pygame.transform.scale(assets[MAUA_SHOOT_IMG], size)
        # Lançando laser
        self.maua_laser_img_0 = pygame.transform.scale(assets[MAUA_LASER_IMG_0], size)
        self.maua_laser_img_1 = pygame.transform.scale(assets[MAUA_LASER_IMG_1], size)
        self.maua_laser_img_2 = pygame.transform.scale(assets[MAUA_LASER_IMG_2], size)
        # Imagem do laser
        self.laser_pre_img = pygame.transform.scale(assets[LASER_IMG_0], (WIDTH, MAUA_SIZE))
        self.laser_img = pygame.transform.scale(assets[LASER_IMG_1], (WIDTH, MAUA_SIZE*2))
        # Imagem da bala
        self.bullet_img = pygame.transform.scale(assets[MAUA_BULLET_IMG], size)

        # Anexo da imagem inicial
        # Começa com a invertida para que ele fique
        # virado à esquerda
        self.image = pygame.transform.flip(self.idle_img, True, False)

        # Controle do tempo dos frames
        self.last_frame = 0
        # Controle do frame atual
        self.current_frame = 0

        # Direção da imagem e do tiro
        self.dir = -1

        self.rect = self.image.get_rect()

        self.rect.right = WIDTH - self.rect.width*2
        self.rect.bottom = HEIGHT - TILE_SIZE

        # Definição da vida inicial do boss
        self.hp = 100
        # Vivo ou não. Usada para checar o estado
        # fora do boss
        self.alive = True

        # -- Definição dos estados do boss
        # Parado
        self.idle_state = 'idle'
        # Andando
        self.walk_state = 'walk'
        # Atirando
        self.shoot_state = 'shoot'
        # Laser
        self.laser_state = 'laser'
        # Morto. Esse estado é usado para quando
        # a vida do boss zera, ao invés de apenas
        # "apagá-lo" da tela
        self.dead_state = 'dead'
        # Lista que contém todos os estados normais
        # o estado "morto" não está aqui pois não
        # é acessado pelo boss em seu ciclo padrão
        self.all_states = [self.idle_state, self.walk_state, self.shoot_state, self.laser_state]
        # Estado atual
        self.state = self.all_states[0]

        # -- Variáveis de estado
        # - Walk
        # Velocidade de andar
        self.walk_speed = MAUA_SPD

        # - Shoot
        # Tempo desde o último tiro
        self.last_shot = 0
        # Cooldown entre os tiros
        self.shot_cd = MAUA_BULLET_CD

        # - Laser
        # Controla se o laser existe ou não
        self.laser_exists = False
        # Tempo desde o início do carregamento
        self.laser_init = 0
        # Tempo para carregar o laser
        self.laser_powerup = 3000
        # Duração do laser
        self.laser_duration = 3000
        
        # Variável para controlar o tempo desde o último estado
        self.last_state = 0
        # Dicionário para definir o tempo de cada estado
        self.times = {
            self.idle_state: 3 * 1000,
            self.walk_state: 4 * 1000,
            self.shoot_state: 3 * 1000,
            self.laser_state: 1 * 1000 + self.laser_powerup + self.laser_duration, # 2s a mais que o tempo total do laser
            self.dead_state: 100 * 1000
        }
    # Método em que o Mauazinho fica parado.
    def idle(self):
        
        # Não faz nada
        self.image = self.image

    # Método em que o Mauazinho anda pela tela
    # ele sempre se mantém dentro dos limites
    def walk(self):
        
        # Pega o tick atual
        now = pygame.time.get_ticks()
        # Vê quanto tempo passou desde o último frame
        elapsed_time = now - self.last_frame

        image = self.image
        # Se o tempo entre os frames passar do fps
        if elapsed_time > self.walk_fps:
            # Se o frame for o 1º, normal ou invertido...
            if self.current_frame == 0:
                # Troca a imagem para o 2º de acordo com a direção
                # À direita
                if self.dir > 0:
                    image = self.walk_img1
                # À esquerda
                else:
                    image = pygame.transform.flip(self.walk_img1, True, False)
                
                # Atualiza o frame atual
                self.current_frame = 1
            # Se for o 2º
            else:
                # Troca a imagem para o 1º de acordo com a direção
                # À direita
                if self.dir > 0:
                    image = self.walk_img0
                # À esquerda
                else:
                    image = pygame.transform.flip(self.walk_img0, True, False)
                
                # Atualiza o frame atual
                self.current_frame = 0
            
            self.last_frame = now

        # Inverte o movimento e a imagem do boss
        # Se o sprite estiver fora da tela...
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            # Inverte a direção do movimento
            self.dir *= -1

            image = pygame.transform.flip(image, self.dir, False)

        # Atualiza a imagem caso haja alguma alteração
        self.image = image
        # Atualiza a posição de acordo com a velocidade
        # e a direção
        self.rect.x += self.walk_speed * self.dir
    
    # Método de tiro
    def shoot(self):
        # Pega o tick atual
        now = pygame.time.get_ticks()
        # Vê quanto tempo passou desde o último tiro
        elapsed_time = now - self.last_shot

        # Se o tempo desde o último tiro é maior 
        # que o cooldown entre tiros...
        if elapsed_time > self.shot_cd:
            # Define se as balas surgem para a direita ou esquerda
            # de acordo com a direção
            # Diferença de ângulo entre as balas
            angle_dif = 30
            # Ângulo inicial
            base_angle = 5
            # Se a direção for à esquerda...
            if self.dir < 0:
                # Altera o ângulo base
                base_angle = 180-base_angle + angle_dif*2
            # Gera 3 balas em forma de cone
            for i in range(0, 2+1):
                bullet_angle = base_angle - angle_dif * i
                bullet = Maua_bullet(self.bullet_img, (self.rect.center), bullet_angle)
                # Adiciona-a no grupo de sprites
                self.all_sprites.add(bullet)
                self.all_enemies.add(bullet)
            # Atualiza o tempo do último tiro
            self.last_shot = now

    # Método de laser
    def laser(self):
        # Gera apenas um pré laser
        # o "pré laser" gera o laser danoso
        if self.laser_exists == False:
            # Gera o laser
            laser = Maua_pre_laser([self.laser_pre_img, self.laser_img], (self.rect.center), self.dir, self.laser_powerup, self.laser_duration, self.all_sprites, self.all_enemies)
            # Adiciona-o nos grupos de sprites
            self.all_sprites.add(laser)
            self.all_enemies.add(laser)
            # Atualiza a variável para impedir
            # infinitos lasers
            self.laser_exists = True
    
        # Pega o tick atual
        now = pygame.time.get_ticks()
        # Vê quanto tempo passou desde o último tiro
        elapsed_time = now - self.laser_init

        # Se o tempo passado for maior do que a ativação + duração do laser...
        if elapsed_time > self.laser_duration + self.laser_powerup:
            # Altera a imagem para o sprite sem laser
            # de acordo com a direção
            if self.dir > 0:
                self.image = self.maua_laser_img_0
            else:
                self.image = pygame.transform.flip(self.maua_laser_img_0, True, False)
        # Senão, se for maior que apenas a ativação...
        elif elapsed_time > self.laser_powerup:
            # Muda para a imagem do laser ativo
            # de acordo com a direção
            if self.dir > 0:
                self.image = self.maua_laser_img_2
            else:
                self.image = pygame.transform.flip(self.maua_laser_img_2, True, False)

    def update(self):
        # Pega o tick atual
        now = pygame.time.get_ticks()
        # Vê quanto tempo passou desde o último estado
        elapsed_time = now - self.last_state

        # Se o tempo passou da duração do estado atual...
        if elapsed_time > self.times[self.state]:
            # Guarda o estado atual
            current_state = self.state
            # Muda o estado aleatoriamente
            self.state = random.choice(self.all_states)

            # Enquanto o estado atual for igual ao estado
            # anterior, escolhe de novo
            while self.state == current_state:
                self.state = random.choice(self.all_states)

            # Guarda o momento em que trocou o estado
            self.last_state = now

            # Define a direção da imagem
            img_flip = True
            # Se estiver indo para a direita, a imagem não
            # vai ser invertida
            if self.dir > 0:
                img_flip = False
            
            # De acordo com o estado, altera a imagem
            match self.state:
                case self.idle_state:
                    self.image = pygame.transform.flip(self.idle_img, img_flip, False)
                case self.walk_state:
                    self.image = pygame.transform.flip(self.walk_img0, img_flip, False)

                    # Atualiza o momento do último frame, pois a imagem foi alterada
                    self.last_frame = now
                case self.shoot_state:
                    self.image = pygame.transform.flip(self.shoot_img, img_flip, False)
                case self.laser_state:
                    self.image = pygame.transform.flip(self.maua_laser_img_1, img_flip, False)

                    # - Reset do laser
                    # Confirma que não existe lasers na tela
                    self.laser_exists = False
                    # Determina o momento de início
                    self.laser_init = now                

        # Define o método a ser chamado de acordo com 
        # o estado atual
        match self.state:
            # Parado
            case self.idle_state:
                self.idle()
            # Andando
            case self.walk_state:
                self.walk()
            # Atirando
            case self.shoot_state:
                self.shoot()
            # Laser
            case self.laser_state:
                self.laser()
            # Morto
            case self.dead_state:
                self.dead()

        hits = pygame.sprite.spritecollide(self, self.all_bullets, True)

        for hit in hits:
            self.hit()

        # Se a vida for menor ou igual a zero...
        if self.hp <= 0:
            # Ativa o estado de morte
            self.state = self.dead_state
        
    # Método para levar dano
    def hit(self):

        # Diminui a vida atual
        self.hp -= 1

    # Estado de morte
    def dead(self):

        self.alive = False
        self.image = self.laser_pre_img

class Maua_bullet(pygame.sprite.Sprite):
    def __init__(self, img, coordinates, angle):
        # Construtor da classe pai (Sprite)
        pygame.sprite.Sprite.__init__(self)

        # A imagem já vem transformada pelo 
        # objeto "Mauazinho", então é possível
        # apenas assimila-la

        # Rotaciona a bala de acordo com o ângulo fornecido
        self.image = pygame.transform.rotate(img, -angle)

        # Define o retângulo da imagem
        self.rect = self.image.get_rect()
        self.rect.center = coordinates

        # Define a velocidade da bala
        speed = MAUA_BULLET_SPD

        # - Decompõe o movimento vertical e horizontal
        # ângulo de graus para radianos
        angle = math.radians(angle)
        # Movimento em x
        self.speedx = speed  * math.cos(angle)
        # Movimento em y
        self.speedy = speed * math.sin(angle)
    
    def update(self):

        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class Maua_pre_laser(pygame.sprite.Sprite):
    def __init__(self, images, coordinates, direction, powerup, duration, all_sprites, all_enemies):
        # Construtor da classe pai (Sprite)
        pygame.sprite.Sprite.__init__(self)

        # Armazena as imagens das duas fases do laser
        pre_img = images[0]
        pos_img = images[1]

        # Armazena os argumentos para replicá-los
        # no laser final
        # Coordenadas
        self.coordinates = coordinates
        # Direção
        self.direction = direction
        # Tempo até carregar o laser real
        self.powerup = powerup
        # Duração
        self.duration = duration
        # Grupo com todos os sprites
        self.all_sprites = all_sprites
        # Grupo com as ameaças
        self.all_enemies = all_enemies

        # Variação da direção de acordo com o
        # lado do mauazinho
        # À direita
        if direction > 0:
            # Imagem de aviso
            self.image = pre_img
            # Imagem do laser final
            self.pos_img = pos_img
            # Define o retângulo da imagem
            self.rect = self.image.get_rect()
            # Define a extremidade para a esquerda
            self.rect.midleft = self.coordinates
            self.coordinates = (self.coordinates[0]+10, self.coordinates[1]+20)
        # À esquerda
        else:
            # Imagem de aviso
            self.image = pygame.transform.flip(pre_img, True, False)
            # Imagem do laser final
            self.pos_img = pygame.transform.flip(pos_img, True, False)
            # Define o retângulo da imagem
            self.rect = self.image.get_rect()
            # Define a extremidade para a direita
            self.rect.midright = self.coordinates
            self.coordinates = (self.coordinates[0]-10, self.coordinates[1]+20)
            

        # Determina o tempo em que o laser surgiu
        self.init = pygame.time.get_ticks()

    def update(self):

        # Pega o tick atual
        now = pygame.time.get_ticks()
        # Vê quanto tempo passou desde o começo
        # do carregamento
        elapsed_time = now - self.init

        # Se o tempo desde o início superar a duração...
        if elapsed_time > self.powerup:
            # Gera o laser real
            laser = Maua_laser(self.pos_img, self.coordinates, self.direction, self.duration)
            # Adiciona o laser aos grupos de sprites
            self.all_sprites.add(laser)
            self.all_enemies.add(laser)
            # Apaga o laser
            self.kill()

class Maua_laser(pygame.sprite.Sprite):
    def __init__(self, img, coordinates, direction, duration):
        # Construtor da classe pai (Sprite)
        pygame.sprite.Sprite.__init__(self)

        # A imagem já vem transformada pelo 
        # objeto "Mauazinho", então é possível
        # apenas assimila-la
        # Contudo, varia de acordo com a direção.
        # Também define a posição inicial
        # À direita
        if direction > 0:
            self.image = img
            # Define o retângulo da imagem
            self.rect = self.image.get_rect()
            # Define a extremidade para a esquerda
            self.rect.midleft = coordinates
        # À esquerda
        else:
            self.image = pygame.transform.flip(img, True, False)
            # Define o retângulo da imagem
            self.rect = self.image.get_rect()
            # Define a extremidade para a direita
            self.rect.midright = coordinates
        
        # Define o tempo de duração do laser
        # Após esse tempo, ele é apagado
        self.duration = duration

        # Determina o tempo em que o laser surgiu
        self.init = pygame.time.get_ticks()

    def update(self):

        # Pega o tick atual
        now = pygame.time.get_ticks()
        # Vê quanto tempo passou desde o começo
        # do carregamento
        elapsed_time = now - self.init

        # Se o tempo desde o início superar a duração...
        if elapsed_time > self.duration:
            # Apaga o laser
            self.kill()
