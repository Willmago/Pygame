# --- Importa e inicia pacotes
import pygame
import math
from config import *
import random

# Essa função é passada como o argumento 'collided' da
# função pygame.sprite.spritecollide ou groupcollide
def collided(sprite, other):
    # Checa se as hitbox de dois sprites colidiram
    return sprite.hitbox.colliderect(other.hitbox)
# De https://gamedev.stackexchange.com/questions/159082/adjusting-collision-hitbox-size-with-pygame

# Classe que representa os blocos do cenário
class Tile(pygame.sprite.Sprite):

    # Construtor da classe
    def __init__(self, tile_img, row, colum):
        # Construtor da classe pai (Sprite)
        pygame.sprite.Sprite.__init__(self)

        if tile_img is None:
            # Plataforma invisível: surface transparente
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))
        else:
            # Aumenta o tamanho do tile
            tile_img = pygame.transform.scale(tile_img, (TILE_SIZE, TILE_SIZE))
            self.image = tile_img

        # Detalhes sobre o posicionamento
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

        #region definições iniciais
        # Define o estado autal
        # usado para determinar as ações disponíveis para o jogador
        self.state = STILL # Começa imóvel

        # Ajusta o tamanho da imagem
        self.player_img = pygame.transform.scale(player_img, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.img_flipped = pygame.transform.flip(self.player_img, True, False)

        # Define a imagem do sprite
        self.image = self.player_img
        # Detalhes sobre o posicionamento
        self.rect = self.image.get_rect()
        #endregion
        #region Posição
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
        #endregion

        #imagem bala
        self.bulletimg = assets[BULLET1]

        #som bala
        self.bullet_snd = assets[SHOOT_SND]
        self.bullet_snd.set_volume(0.08)

        #dicionário assets
        self.all_sprites = all_groups['all_sprites']

        #grupo balas
        self.all_bullets = all_groups['all_bullets']

        #grupo inimigos
        self.all_enemies = all_groups['all_enemies']

        #region - Vida
        # Hitbox
        self.hitbox = self.rect.inflate(-50, -20)
        # Vida inicial
        self.hp = PLAYER_HP
        # Tempo de invulnerabilidade
        self.i_frames = I_FRAMES
        # Momento do último hit. Usado
        # para determinar se pode ou não
        # levar dano
        self.last_hit = 0
        # Controle da vulnerabilidade do
        # personagem
        self.invincible = False
        # Vivo ou não. Usado para definir
        # se pode ou não controlá-lo
        self.alive = True
        #endregion

        # Marca o tempo do último tiro (em ms)
        self.last_shot = 0

        # Tamanho do pulo (pode ser sobrescrito por fase)
        self.jump_size = JUMP_SIZE

        # Contador de frames para ignorar plataformas ao descer
        self.drop_timer = 0

        # Limite inferior do player (None = usa HEIGHT)
        self.floor_y = None
    
    # Método que atualiza a posição do personagem
    def update(self):

        # Atualiza a posição da hitbox
        self.hitbox.center = self.rect.center
        
        #region -- Movimento em y
        # Dispara enquanto o botão esquerdo do mouse estiver pressionado
        # E o player estiver vivo
        if pygame.mouse.get_pressed()[0] and self.alive == True:
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
        if self.drop_timer > 0:
            self.drop_timer -= 1

        if self.speedy > 0 and self.drop_timer == 0:
            collisions = pygame.sprite.spritecollide(self, self.platforms, False)
            for platform in collisions:
                if self.highest_y <= platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.speedy = 0
                    self.state = STILL
        #endregion

        #region -- Limites da tela
        max_bottom = self.floor_y if self.floor_y is not None else HEIGHT

        if self.rect.top < 0:
            self.rect.top = 0
            self.speedy = 0
        if self.rect.bottom > max_bottom:
            self.rect.bottom = max_bottom
            self.speedy = 0
            self.state = STILL
            self.drop_timer = 0
        #endregion
        #region -- Movimento em x --
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
        #endregion

        #region -- Hit
        # Pega o momento atual
        now = pygame.time.get_ticks()
        # Vê o tempo desde o último hit
        elapsed = now - self.last_hit
        # Se o tempo for maior que o de invulnerabilidade
        if elapsed > self.i_frames:
            
            self.invincible = False
            # Veficia colisões com inimigos
            hits = pygame.sprite.spritecollide(self, self.all_enemies, False, collided)
            # se tiver sido acertado e não estiver morto...
            if len(hits) != 0 and self.alive == True:
                
                # Perde vida
                self.hp -= 1
                # atualiza o momento do último hit
                self.last_hit = now
                # determina que o player está invulnerável
                self.invincible = True

        # Se a vida for zerada...
        if self.hp <= 0:
            # Player está morto
            self.alive = False
            # garante que ele não vai se mover em x
            self.speedx = 0

        if self.invincible == True:
            alpha = 100 * math.sin(now * (25/1000)) + 155
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)
        #endregion
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
                self.blocks
            )
            self.all_bullets.add(new_bullet)
            self.all_sprites.add(new_bullet)

            
            self.bullet_snd.play()
     
    # Método que faz o personagem pular
    def jump(self):
        if self.state == STILL:
            self.speedy -= self.jump_size
            self.state = JUMPING
    
class Bullet(pygame.sprite.Sprite):
    # Construtor da classe.
    # origin_x, origin_y: ponto de saída do tiro (já calculado pelo Player)
    # target_x, target_y: posição do cursor (alvo)
    # blocks: grupo de blocos sólidos do mapa para colisão
    def __init__(self, bullet_img, origin_x, origin_y, target_x, target_y, blocks):
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

        # Hitbox
        self.hitbox = self.rect.inflate(-20, -20)

        # Posição em float para movimento suave e preciso
        self.pos_x = float(origin_x)
        self.pos_y = float(origin_y)

    def update(self):
        # Move a bala
        self.pos_x += self.vx
        self.pos_y += self.vy
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

        # Atualiza a hitbox
        self.hitbox.center = self.rect.center

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

    # Só executa as ações se o player estiver vivo
    if player.alive == True:
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
            # - Descer da plataforma
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                player.drop_timer = 12
                player.speedy = 5

        # Verifica se soltou alguma tecla.
        if event.type == pygame.KEYUP:
            # Dependendo da tecla, altera o estado do jogador.
            # - Para movimento para esquerda
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                player.speedx += SPEED_X
            # - Para movimento para a direita
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                player.speedx -= SPEED_X

# Classe que representa o chefe "mauazinho"
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
        bullet_size = (MAUA_BULLET_SIZE, MAUA_BULLET_SIZE)
        #region -- Definição das imagens
        # Imagem normal
        self.idle_img = pygame.transform.scale(assets[MAUA_IDLE_IMG], size)
        # Andando
        self.walk_img0 = pygame.transform.scale(assets[MAUA_WALK_IMG_0], size)
        self.walk_img1 = pygame.transform.scale(assets[MAUA_WALK_IMG_1], size)
        self.walk_fps = 0.2 * 1000
        # Atirando
        self.shoot_img = pygame.transform.scale(assets[MAUA_SHOOT_IMG], size)
        # Lançando laser
        self.maua_laser_img_0 = pygame.transform.scale(assets[MAUA_LASER_IMG_0], size)
        self.maua_laser_img_1 = pygame.transform.scale(assets[MAUA_LASER_IMG_1], size)
        self.maua_laser_img_2 = pygame.transform.scale(assets[MAUA_LASER_IMG_2], size)
        # Morto
        self.dead_img = pygame.transform.scale(assets[MAUA_DEAD_IMG], size)
        # Imagem do laser
        self.laser_pre_img = pygame.transform.scale(assets[LASER_IMG_0], (WIDTH, MAUA_SIZE))
        self.laser_img = pygame.transform.scale(assets[LASER_IMG_1], (WIDTH, MAUA_SIZE*2))
        # Imagens da bala
        self.bullet_imgs = [
            pygame.transform.scale(assets[MAUA_BULLET_IMG_0], bullet_size),
            pygame.transform.scale(assets[MAUA_BULLET_IMG_1], bullet_size),
            pygame.transform.scale(assets[MAUA_BULLET_IMG_2], bullet_size)
        ]
        #endregion

        #region -- Sons
        # Carrega o som
        # Define seu volume
        # Andar
        self.walk_snd = assets[MAUA_WALK_SND]
        self.walk_snd.set_volume(1)
        # Disparo
        self.shot_snd = assets[MAUA_SHOT_SND]
        self.shot_snd.set_volume(0.25)
        # Variação do disparo
        self.shot_snd1 = assets[MAUA_SHOT_SND1]
        self.shot_snd1.set_volume(0.25)
        # Laser
        self.laser_snd = assets[MAUA_LASER_SND]
        self.laser_snd.set_volume(0.3)
        #endregion

        #region variáveis de imagem
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

        # Retângulo que envolve a imagem
        self.rect = self.image.get_rect()

        # Define a posição inicial
        self.rect.right = WIDTH - self.rect.width*2
        self.rect.bottom = HEIGHT - TILE_SIZE * 5
        #endregion

        #region Vida
        # Hitbox
        self.hitbox = self.rect.inflate(-20, 0)
        # Definição da vida inicial do boss
        self.max_hp = MAUA_HP
        self.hp = self.max_hp
        # Vivo ou não. Usada para checar o estado
        # fora do boss
        self.alive = True
        #endregion

        #region -- Definição dos estados do boss
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
        # Lista que contém todos os estados normais.
        # O estado "morto" não está aqui pois não
        # é acessado pelo boss em seu ciclo padrão.
        # Alguns estão repetidos para diminuir a 
        # frequência de "idle"
        self.all_states = [self.idle_state, self.walk_state, self.shoot_state, self.laser_state, self.walk_state, self.shoot_state] #[self.idle_state, self.walk_state, self.shoot_state, self.laser_state, self.walk_state, self.shoot_state, self.laser_state]
        # Estado atual
        self.state = self.walk_state
        #endregion

        #region -- Variáveis de estado
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
        self.laser_powerup = MAUA_LASER_POWERUP
        # Duração do laser
        self.laser_duration = MAUA_LASER_DURATION
        
        # Variável para controlar o tempo desde o último estado
        self.last_state = 0
        # Dicionário para definir o tempo de cada estado
        self.times = {
            self.idle_state: 1.5 * 1000,
            self.walk_state: 3 * 1000,
            self.shoot_state: 3 * 1000,
            self.laser_state: 0.5 * 1000 + self.laser_powerup + self.laser_duration, # 2s a mais que o tempo total do laser
            self.dead_state: 100 * 1000
        }
        #endregion
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
            
            # Atualiza o momento do último frame
            self.last_frame = now
            # Toca o som de passo
            self.walk_snd.play()

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
            # número de balas
            bullet_num = MAUA_BULLET_COUNT
            # Define se as balas surgem para a direita ou esquerda
            # de acordo com a direção
            # Diferença de ângulo entre as balas
            angle_dif = 35
            # Ângulo inicial
            base_angle = 5
            multiplier = 1
            # Se a direção for à esquerda...
            if self.dir < 0:
                # Altera o ângulo base
                base_angle = 180 - base_angle

                multiplier = -1
            # Gera 3 balas em forma de cone
            for i in range(bullet_num):
                
                bullet_angle = base_angle - angle_dif * i * multiplier
                bullet = Maua_bullet(self.bullet_imgs, (self.rect.center), bullet_angle)
                # Adiciona-a no grupo de sprites
                self.all_sprites.add(bullet)
                self.all_enemies.add(bullet)
            
            # Escolhe um som aleatório do tiro para evitar
            # fadiga auditiva
            sound = random.choice([self.shot_snd, self.shot_snd1])
            # Toca o som de tiro
            sound.play()
            # Atualiza o tempo do último tiro
            self.last_shot = now

    # Método de laser
    def laser(self):
        # Gera apenas um pré laser
        # o "pré laser" gera o laser danoso
        if self.laser_exists == False:
            # Gera o laser
            laser = Maua_pre_laser(
                [self.laser_pre_img, self.laser_img],
                self.laser_snd, 
                (self.rect.center), 
                self.dir, 
                self.laser_powerup, 
                self.laser_duration, 
                self.all_sprites, 
                self.all_enemies)
            # Adiciona-o no grupo de sprites
            self.all_sprites.add(laser)
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

        #region Dano
        hits = pygame.sprite.spritecollide(self, self.all_bullets, True, collided)

        for hit in hits:
            # Diminui a vida atual
            self.hp -= 1

        # Se a vida for menor ou igual a zero...
        if self.hp <= 0:
            # Ativa o estado de morte
            self.state = self.dead_state
            # Remove o boss do grupo de ameaças
            # para impedir o player de morrer
            self.all_enemies.remove(self)
        
        self.hitbox.center = self.rect.center
        #endregion

    # Estado de morte
    def dead(self):

        self.alive = False
        if self.dir > 0:
            self.image = self.dead_img
        else:
            self.image = pygame.transform.flip(self.dead_img, True, False)

# Classe que representa os tiros do mauazinho
class Maua_bullet(pygame.sprite.Sprite):
    def __init__(self, img, coordinates, angle):
        # Construtor da classe pai (Sprite)
        pygame.sprite.Sprite.__init__(self)

        # As imagens já vem transformadas pelo 
        # objeto "Mauazinho", então é possível
        # apenas assimila-la e rotacionar

        # Rotaciona a bala de acordo com o ângulo fornecido
        # É uma lista para animação
        self.images = [
            pygame.transform.rotate(img[0], -angle),
            pygame.transform.rotate(img[1], -angle),
            pygame.transform.rotate(img[2], -angle)
        ]
        # Determina a imagem inicial
        self.image = self.images[0]

        # Tempo entre frames
        self.fps = 0.1 * 1000   # Segundos x ticks
        # Momento do último frame
        self.last_frame = 0

        # Define o retângulo da imagem
        self.rect = self.image.get_rect()
        self.rect.center = coordinates

        # Hitbox
        self.hitbox = self.rect.inflate(-30, -30)

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

        # Atualiza a hitbox
        self.hitbox.center = self.rect.center

        now = pygame.time.get_ticks()

        elapsed_time = now - self.last_frame

        if elapsed_time > self.fps:
            
            index = self.images.index(self.image) + 1
            if index >= len(self.images):
                index = 0

            self.image = self.images[index]

            self.last_frame = now
        
        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

# Classe que representa o aviso de laser do mauazinho
class Maua_pre_laser(pygame.sprite.Sprite):
    def __init__(self, images, sound, coordinates, direction, powerup, duration, all_sprites, all_enemies):
        # Construtor da classe pai (Sprite)
        pygame.sprite.Sprite.__init__(self)

        # Armazena as imagens das duas fases do laser
        pre_img = images[0]
        pos_img = images[1]

        # Armazena o som do laser
        self.sound = sound

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
            
        # Hitbox
        self.hitbox = self.rect.inflate(-20, -20)

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
            laser = Maua_laser(self.pos_img, self.sound, self.coordinates, self.direction, self.duration)
            # Adiciona o laser aos grupos de sprites
            self.all_sprites.add(laser)
            self.all_enemies.add(laser)
            # Apaga o laser
            self.kill()

# Classe que representa o laser do mauazinho
class Maua_laser(pygame.sprite.Sprite):
    def __init__(self, img, sound, coordinates, direction, duration):
        # Construtor da classe pai (Sprite)
        pygame.sprite.Sprite.__init__(self)

        # Toca o som do laser
        sound.play()

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
        
        # Hitbox
        self.hitbox = self.rect.inflate(-10, -120)

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

# Desenha a barra de vida do boss no topo da tela.
def draw_boss_hp(surface, boss):
    
    bar_w = 500
    bar_h = 22
    x     = (WIDTH - bar_w) // 2
    y     = 18
    ratio = boss.hp / boss.max_hp
    pygame.draw.rect(surface, (60, 20, 20),    (x, y, bar_w, bar_h),              border_radius=5)
    pygame.draw.rect(surface, (220, 50, 50),   (x, y, int(bar_w * ratio), bar_h), border_radius=5)
    pygame.draw.rect(surface, (255, 255, 255), (x, y, bar_w, bar_h), 2,           border_radius=5)
    font  = pygame.font.SysFont(None, 26)
    label = font.render('CHEFÃO', True, (255, 255, 255))
    surface.blit(label, (x + bar_w // 2 - label.get_width() // 2, y + 2))

# ===========================================================================
# BOSS 3 — Rato no Robô
# ===========================================================================

# ---------------------------------------------------------------------------
# Mine — fica estática no chão; explode ao ser acertada por bala do player
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Explosion — sprite temporário que aparece quando uma mina explode
# ---------------------------------------------------------------------------
class Explosion(pygame.sprite.Sprite):

    def __init__(self, explosion_img, cx, cy):
        pygame.sprite.Sprite.__init__(self)
        self.image      = pygame.transform.scale(explosion_img, (EXPLOSION_SIZE, EXPLOSION_SIZE)).convert_alpha()
        self.rect       = self.image.get_rect(center=(cx, cy))
        self._born      = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self._born >= EXPLOSION_DURATION:
            self.kill()


class Mine(pygame.sprite.Sprite):

    def __init__(self, mine_img, explosion_img, x, y, all_sprites):
        pygame.sprite.Sprite.__init__(self)
        self.image         = pygame.transform.scale(mine_img, (MINE_SIZE, MINE_SIZE)).convert_alpha()
        self.rect          = self.image.get_rect()
        self.rect.midbottom = (x, y)
        self._explosion_img = explosion_img
        self._all_sprites   = all_sprites

    def explode(self):
        """Cria o sprite de explosão centralizado na mina e remove a mina."""
        exp = Explosion(self._explosion_img, self.rect.centerx, self.rect.centery)
        self._all_sprites.add(exp)
        self.kill()


# ---------------------------------------------------------------------------
# NailProjectile — prego disparado pelo boss, voa horizontalmente
# ---------------------------------------------------------------------------
class NailProjectile(pygame.sprite.Sprite):

    def __init__(self, nail_img, x, y, vx, vy, blocks):
        pygame.sprite.Sprite.__init__(self)
        self.blocks = blocks
        img = pygame.transform.scale(nail_img, (NAIL_WIDTH, NAIL_HEIGHT))
        # Rotaciona o sprite na direção do disparo
        import math
        angle = -math.degrees(math.atan2(vy, vx))
        img   = pygame.transform.rotate(img, angle)
        self.image = img.convert_alpha()
        self.rect  = self.image.get_rect(center=(x, y))
        self.vx    = vx
        self.vy    = vy

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.top > HEIGHT:
            self.kill()
            return
        if pygame.sprite.spritecollide(self, self.blocks, False):
            self.kill()


# ---------------------------------------------------------------------------
# GearProjectile — engrenagem lançada para cima em arco, cai por gravidade
# ---------------------------------------------------------------------------
class GearProjectile(pygame.sprite.Sprite):

    def __init__(self, gear_img, x, y, vx, blocks):
        pygame.sprite.Sprite.__init__(self)
        self.blocks     = blocks
        self.base_image = pygame.transform.scale(gear_img, (GEAR_SIZE, GEAR_SIZE)).convert_alpha()
        self.image      = self.base_image.copy()
        self.rect       = self.image.get_rect(center=(x, y))
        self.vx         = vx
        self.vy         = -GEAR_THROW_SPEED
        self.pos_x      = float(x)
        self.pos_y      = float(y)
        self.angle      = 0.0

    def update(self):
        self.vy    += GRAVITY * 0.5
        self.pos_x += self.vx
        self.pos_y += self.vy
        self.angle  = (self.angle + 6) % 360
        self.image  = pygame.transform.rotate(self.base_image, self.angle)
        self.rect   = self.image.get_rect(center=(int(self.pos_x), int(self.pos_y)))
        if self.pos_y > HEIGHT + 50 or self.pos_x < -50 or self.pos_x > WIDTH + 50:
            self.kill()
            return
        if pygame.sprite.spritecollide(self, self.blocks, False):
            self.kill()


# ---------------------------------------------------------------------------
# Boss3 — Rato no robô: máquina de estados completa
# ---------------------------------------------------------------------------
class Boss3(pygame.sprite.Sprite):

    def __init__(self, boss_img, boss_walk_img, boss_nail_img, boss_wrench_img, boss_dead_img, boss_gear_img, x, y, blocks, platforms,
                 nail_img, gear_img, mine_img, explosion_img, wrench_slash_img,
                 enemy_projectiles, mines_group, all_sprites):
        pygame.sprite.Sprite.__init__(self)

        # --- Sprites por estado ---
        # Idle / pausa
        img_idle              = pygame.transform.scale(boss_img, (BOSS3_WIDTH, BOSS3_HEIGHT))
        self.img_idle_r       = img_idle
        self.img_idle_l       = pygame.transform.flip(img_idle, True, False)

        # Andando: sprite único
        img_walk        = pygame.transform.scale(boss_walk_img, (BOSS3_WIDTH, BOSS3_HEIGHT))
        self.walk_img_r = img_walk
        self.walk_img_l = pygame.transform.flip(img_walk, True, False)

        # Atirando prego
        img_nail              = pygame.transform.scale(boss_nail_img, (BOSS3_WIDTH, BOSS3_HEIGHT))
        self.img_nail_r       = img_nail
        self.img_nail_l       = pygame.transform.flip(img_nail, True, False)

        # Golpe da chave
        img_wrench            = pygame.transform.scale(boss_wrench_img, (BOSS3_WIDTH, BOSS3_HEIGHT))
        self.img_wrench_r     = img_wrench
        self.img_wrench_l     = pygame.transform.flip(img_wrench, True, False)

        # Flash (telegraph) — tinta vermelha sobre o sprite de chave
        self.img_wrench_flash_r = self._tint(self.img_wrench_r.copy(), (220, 60, 60))
        self.img_wrench_flash_l = self._tint(self.img_wrench_l.copy(), (220, 60, 60))

        # Derrotado
        dead_w = int(BOSS3_WIDTH * 1.4)
        dead_h = int(BOSS3_HEIGHT * 0.6)
        self.img_dead = pygame.transform.scale(boss_dead_img, (dead_w, dead_h))

        # Jogando engrenagens
        img_gear_atk        = pygame.transform.scale(boss_gear_img, (BOSS3_WIDTH, BOSS3_HEIGHT))
        self.img_gear_r     = img_gear_atk
        self.img_gear_l     = pygame.transform.flip(img_gear_atk, True, False)

        self.image = self.img_idle_r
        self.rect  = self.image.get_rect()
        self.rect.midbottom = (x, y)

        # Física
        self.blocks    = blocks
        self.platforms = platforms
        self.pos_x     = float(self.rect.x)
        self.pos_y     = float(self.rect.y)
        self.direction = -1          # começa virado para a esquerda (encarando o player)
        self.speedy    = 0.0

        # Vida
        self.hp     = BOSS3_HP
        self.max_hp = BOSS3_HP
        self.alive  = True

        # Assets de projéteis e minas
        self.nail_img      = nail_img
        self.gear_img      = gear_img
        self.mine_img      = mine_img
        self.explosion_img = explosion_img

        # Sprite do golpe da chave escalado para cada direção
        slash_r              = pygame.transform.scale(wrench_slash_img, (WRENCH_REACH, WRENCH_REACH)).convert_alpha()
        self._wrench_slash_r = slash_r
        self._wrench_slash_l = pygame.transform.flip(slash_r, True, False)

        # Grupos
        self.enemy_projectiles = enemy_projectiles
        self.mines_group       = mines_group
        self.all_sprites       = all_sprites
        self.player_ref        = None  # setado após criação do player

        # Máquina de estados
        self.state        = BOSS_WALKING
        self.state_timer  = pygame.time.get_ticks()
        # Primeiro alvo: canto esquerdo
        self.walk_target  = BOSS3_WIDTH // 2 + 20

        # Parada mid-walk
        self.walk_start_time   = pygame.time.get_ticks()
        self.next_midwalk_stop = random.randint(1500, 3000)

        # Minas
        self.last_mine_x   = -999
        self.mine_interval = 180

        # Ataque de pregos
        self.nail_count    = 0
        self.nail_max      = 5
        self.nail_interval = 600
        self.last_nail_t   = 0

        # Ataque de engrenagens
        self.gear_count    = 0
        self.gear_max      = 6
        self.gear_interval = 350
        self.last_gear_t   = 0

        # Flash do telegraph
        self.flash_visible  = True
        self.flash_timer    = 0
        self.flash_interval = 200

    @staticmethod
    def _tint(surface, color):
        tinted = surface.copy()
        tinted.fill(color, special_flags=pygame.BLEND_RGB_MULT)
        return tinted

    def take_damage(self, amount=1):
        self.hp = max(0, self.hp - amount)
        if self.hp == 0:
            self.alive = False
            # Troca para sprite de derrotado e reposiciona no chão
            old_bottom    = self.rect.bottom
            self.image    = self.img_dead
            self.rect     = self.image.get_rect()
            self.rect.bottom = old_bottom
            # Não chama kill() ainda — fica visível até a tela de vitória

    def update(self):
        if not self.alive:
            return  # sprite de derrotado já foi definido em take_damage

        now     = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        # Gravidade — boss fica no chão (colide com blocks e platforms invisíveis)
        self.speedy += GRAVITY
        self.pos_y  += self.speedy
        self.rect.y  = int(self.pos_y)
        ground_hits = list(pygame.sprite.spritecollide(self, self.blocks, False)) +                       list(pygame.sprite.spritecollide(self, self.platforms, False))
        for c in ground_hits:
            if self.speedy > 0:
                self.rect.bottom = c.rect.top
                self.pos_y       = float(self.rect.y)
                self.speedy      = 0
                break

        # --- Estado: caminhando
        if self.state == BOSS_WALKING:
            self._walk()
            self._try_drop_mine()
            if abs(self.rect.x - self.walk_target) < BOSS3_SPEED + 2:
                self.rect.x      = self.walk_target
                self.pos_x       = float(self.rect.x)
                self.state       = BOSS_PAUSE
                self.state_timer = now
            elif now - self.walk_start_time >= self.next_midwalk_stop:
                self.state       = BOSS_PAUSE
                self.state_timer = now

        # --- Pausa antes do ataque
        elif self.state == BOSS_PAUSE:
            self._set_sprite()
            if elapsed >= ATTACK_COOLDOWN // 2:
                self._choose_attack(now)

        # --- Telegraph da chave (pisca vermelho)
        elif self.state == BOSS_TELEGRAPH:
            if now - self.flash_timer > self.flash_interval:
                self.flash_visible = not self.flash_visible
                self.flash_timer   = now
            self._set_sprite(flash=not self.flash_visible)
            if elapsed >= WRENCH_TELEGRAPH:
                self.state       = BOSS_WRENCH
                self.state_timer = now
                self.flash_visible = True

        # --- Golpe da chave (hitbox ativo)
        elif self.state == BOSS_WRENCH:
            self._set_sprite()
            if elapsed >= WRENCH_ACTIVE:
                self._end_attack(now)

        # --- Ataque de pregos
        elif self.state == BOSS_NAILS:
            self._set_sprite()
            if now - self.last_nail_t >= self.nail_interval:
                self._shoot_nail()
                self.last_nail_t = now
                self.nail_count += 1
            if self.nail_count >= self.nail_max:
                self._end_attack(now)

        # --- Ataque de engrenagens
        elif self.state == BOSS_GEARS:
            self._set_sprite()
            if now - self.last_gear_t >= self.gear_interval:
                self._throw_gear()
                self.last_gear_t = now
                self.gear_count += 1
            if self.gear_count >= self.gear_max:
                self._end_attack(now)

    # --- Helpers internos ---

    def _walk(self):
        dx = self.walk_target - self.rect.x
        if dx > 0:
            self.direction = 1
            self.pos_x    += BOSS3_SPEED
        else:
            self.direction = -1
            self.pos_x    -= BOSS3_SPEED
        self.rect.x = int(self.pos_x)
        self.image = self.walk_img_r if self.direction == 1 else self.walk_img_l

    def _try_drop_mine(self):
        if abs(self.rect.centerx - self.last_mine_x) >= self.mine_interval:
            mine = Mine(self.mine_img, self.explosion_img,
                        self.rect.centerx, self.rect.bottom, self.all_sprites)
            self.mines_group.add(mine)
            self.all_sprites.add(mine)
            self.last_mine_x = self.rect.centerx

    def _choose_attack(self, now):
        attack = random.choice([BOSS_TELEGRAPH, BOSS_NAILS, BOSS_GEARS])
        self.state        = attack
        self.state_timer  = now
        self.flash_timer  = now
        self.nail_count   = 0
        self.gear_count   = 0
        self.last_nail_t  = now
        self.last_gear_t  = now
        # Vira para encarar o centro da tela
        self.direction = -1 if self.rect.centerx > WIDTH // 2 else 1

    def _end_attack(self, now):
        if self.rect.centerx < WIDTH // 2:
            self.walk_target = WIDTH - BOSS3_WIDTH - 20
        else:
            self.walk_target = BOSS3_WIDTH // 2 + 20
        self.state             = BOSS_WALKING
        self.state_timer       = now
        self.walk_start_time   = now
        self.next_midwalk_stop = random.randint(1500, 3000)

    def _shoot_nail(self):
        ox = self.rect.right if self.direction == 1 else self.rect.left
        oy = self.rect.centery - 20
        # Mira no jogador se disponível
        if self.player_ref is not None:
            px = self.player_ref.rect.centerx
            py = self.player_ref.rect.centery
            dx = px - ox
            dy = py - oy
            dist = max(1, (dx**2 + dy**2) ** 0.5)
            vx = NAIL_SPEED * dx / dist
            vy = NAIL_SPEED * dy / dist
        else:
            vx = NAIL_SPEED * self.direction
            vy = 0
        nail = NailProjectile(self.nail_img, ox, oy, vx, vy, self.blocks)
        self.enemy_projectiles.add(nail)
        self.all_sprites.add(nail)

    def _throw_gear(self):
        spread = WIDTH // (self.gear_max + 1)
        tx = spread * (self.gear_count + 1)
        ox = self.rect.centerx
        vx = (tx - ox) / 30
        gear = GearProjectile(self.gear_img, ox, self.rect.top - 20, vx, self.blocks)
        self.enemy_projectiles.add(gear)
        self.all_sprites.add(gear)

    def _set_sprite(self, flash=False):
        right = (self.direction == 1)
        if self.state == BOSS_NAILS:
            new_img = self.img_nail_r  if right else self.img_nail_l
        elif self.state in (BOSS_WRENCH, BOSS_TELEGRAPH):
            if flash:
                new_img = self.img_wrench_flash_r if right else self.img_wrench_flash_l
            else:
                new_img = self.img_wrench_r if right else self.img_wrench_l
        elif self.state == BOSS_GEARS:
            new_img = self.img_gear_r if right else self.img_gear_l
        else:
            new_img = self.img_idle_r if right else self.img_idle_l
        # Troca apenas a imagem — rect permanece o mesmo para não deslocar o boss
        self.image = new_img

    def get_wrench_slash_img(self):
        if self.state != BOSS_WRENCH:
            return None
        return self._wrench_slash_r if self.direction == 1 else self._wrench_slash_l

    def get_wrench_rect(self):
        """Retorna o hitbox da chave quando o golpe está ativo, ou None."""
        if self.state != BOSS_WRENCH:
            return None
        if self.direction == 1:
            return pygame.Rect(self.rect.right, self.rect.top + 20,
                               WRENCH_REACH, self.rect.height // 2)
        else:
            return pygame.Rect(self.rect.left - WRENCH_REACH, self.rect.top + 20,
                               WRENCH_REACH, self.rect.height // 2)


# ===== Gerador de chuva =====
def spawn_rain(n, speed_mult):
    lo, hi = FALL_SPD_MIN*speed_mult, FALL_SPD_MAX*speed_mult
    area_s, area_e = 20, PLATFORM_X - 30
    area_w = area_e - area_s
    gap_s  = random.randint(area_s, area_e - MIN_GAP)
    gap_e  = gap_s + MIN_GAP
    bullets = []
    if n == 0: return bullets
    sw = area_w / n
    for i in range(n):
        lo_s = area_s + i*sw; hi_s = lo_s + sw - BULLET_W
        if hi_s < lo_s: hi_s = lo_s
        cx = (lo_s+hi_s)/2
        if cx+BULLET_W > gap_s and cx < gap_e: continue
        bx_lo = max(int(lo_s), area_s); bx_hi = min(int(hi_s), area_e-BULLET_W)
        if bx_hi > gap_s-BULLET_W and bx_lo < gap_e:
            if bx_lo < gap_s-BULLET_W: bx_hi = gap_s-BULLET_W
            else: bx_lo = gap_e
        if bx_hi < bx_lo: continue
        bx = random.randint(bx_lo, bx_hi)
        by = random.randint(-400, -BULLET_H)
        bullets.append(FallingBullet(bx, by, random.uniform(lo, hi)))
    return bullets

def spawn_diag(n, speed_mult):
    spd = DIAG_SPD * speed_mult
    area_s, area_e = 20, PLATFORM_X - 30
    sw = (area_e-area_s) / max(n,1)
    missiles = []
    for i in range(n):
        bx = random.randint(int(area_s+i*sw), max(int(area_s+i*sw), int(area_s+(i+1)*sw)-BULLET_W))
        bx = max(area_s, min(bx, area_e-BULLET_W))
        missiles.append(DiagonalMissile(bx, -80, spd, 1 if i%2==0 else -1))
    return missiles

# ===== Cenário =====
def draw_background(surf, tick):
    # Apenas a imagem de fundo — sem céu, nuvens, chão ou plataforma desenhados
    surf.blit(bg_image, (0, 0))

def draw_player(surf, x, y, facing, hp, shooting, jumping=False):
    # Sprite original olha para a ESQUERDA
    # facing=-1 (esquerda) → sprite normal
    # facing= 1 (direita)  → sprite espelhado
    if jumping:
        spr = raposa_pulo_flip if facing == 1 else raposa_pulo
    else:
        spr = raposa_sprite_flip if facing == 1 else raposa_sprite
    surf.blit(spr, (int(x), int(y)))
    for i in range(hp):
        draw_heart(surf, int(x) + i*18, int(y) - 22, 8)

def draw_heart(surf,x,y,size):
    pygame.draw.circle(surf,C_RED,(x+size//2,y+size//2),size//2)
    pygame.draw.circle(surf,C_RED,(x+size,   y+size//2),size//2)
    pygame.draw.polygon(surf,C_RED,[(x,y+size//2),(x+size,y+size+size//2),(x+size*2,y+size//2)])

def draw_boss_hpbar(surf, hp):
    if   hp > PHASE2_HP: face = boss_faces[0]
    elif hp > PHASE3_HP: face = boss_faces[1]
    else:                face = boss_faces[2]
    face_h = max(f.get_height() for f in boss_faces)
    bw=300; bx=WIDTH//2-bw//2; by=face_h+16
    pygame.draw.rect(surf,C_OUTLINE,  (bx-2,by-2,bw+4,24))
    pygame.draw.rect(surf,C_DARK_GRAY,(bx,by,bw,20))
    hw = int(bw*hp/BOSS_HP_MAX)
    if hw>0:
        hc = C_GREEN if hp>PHASE2_HP else C_YELLOW if hp>PHASE3_HP else C_RED
        pygame.draw.rect(surf,hc,(bx,by,hw,20),border_radius=2)
    surf.blit(face,(WIDTH//2-face.get_width()//2, by-face.get_height()-4))

def draw_boss_sprite(surf, hp, attacking, tick):
    bob = int(math.sin(tick*0.04)*4) if attacking else 0
    surf.blit(boss_sprite,(BOSS_X,BOSS_Y+bob))
    if attacking and (tick//8)%2==0:
        glow=pygame.Surface((BOSS_W,BOSS_H),pygame.SRCALPHA)
        pygame.draw.circle(glow,(255,220,0,70),(BOSS_W//2,BOSS_H//3),28)
        surf.blit(glow,(BOSS_X,BOSS_Y+bob))
    draw_boss_hpbar(surf,hp)

def draw_hud(surf, score, phase):
    surf.blit(font_med.render(f"SCORE: {score}",True,C_BLACK),(22,52))
    surf.blit(font_med.render(f"SCORE: {score}",True,C_WHITE),(20,50))
    surf.blit(font_small.render(f"Fase: {phase}",True,C_BLACK),(22,92))
    surf.blit(font_small.render(f"Fase: {phase}",True,C_YELLOW),(20,90))

def draw_game_over(surf, win):
    ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
    ov.fill((0,0,0,160)); surf.blit(ov,(0,0))
    msg="VOCÊ VENCEU!" if win else "GAME OVER"
    txt=font_large.render(msg,True,C_YELLOW if win else C_RED)
    surf.blit(font_large.render(msg,True,C_BLACK),(WIDTH//2-txt.get_width()//2+4,HEIGHT//2-44))
    surf.blit(txt,(WIDTH//2-txt.get_width()//2,HEIGHT//2-48))
    sub=font_small.render("R = recomeçar  | Enter = Próxima fase |  ESC = sair",True,C_WHITE)
    surf.blit(sub,(WIDTH//2-sub.get_width()//2,HEIGHT//2+20))

# ===== Projéteis =====
class FallingBullet:
    def __init__(self,x,y,speed):
        self.x=float(x); self.y=float(y); self.speed=speed; self.alive=True
    def update(self): self.y+=self.speed; self.alive=self.y<=HEIGHT
    def rect(self): m=3; return pygame.Rect(int(self.x)+m,int(self.y)+m,BULLET_W-m*2,BULLET_H-m*2)
    def draw(self,surf): surf.blit(missil_fall,(int(self.x),int(self.y)))

class HorizontalMissile:
    def __init__(self,x,y,speed):
        self.x=float(x); self.y=float(y); self.speed=speed; self.alive=True
    def update(self): self.x-=self.speed; self.alive=self.x>-HORIZ_W-20
    def rect(self): m=4; return pygame.Rect(int(self.x)+m,int(self.y)+m,HORIZ_W-m*2,HORIZ_H-m*2)
    def draw(self,surf): surf.blit(missil_horiz,(int(self.x),int(self.y)))

class DiagonalMissile:
    def __init__(self,x,y,speed,direction):
        self.x=float(x); self.y=float(y)
        self.speedy=speed; self.speedx=speed*0.75*direction
        self.sprite=missil_diag_r if direction==1 else missil_diag_l
        self.sw=self.sprite.get_width(); self.sh=self.sprite.get_height()
        self.alive=True
    def update(self):
        self.x+=self.speedx; self.y+=self.speedy
        self.alive=self.y<=HEIGHT and -self.sw-20<self.x<WIDTH+20
    def rect(self): m=8; return pygame.Rect(int(self.x)+m,int(self.y)+m,self.sw-m*2,self.sh-m*2)
    def draw(self,surf): surf.blit(self.sprite,(int(self.x),int(self.y)))

class Bolinha:
    """Bolinha fase 3 — vem da direita na altura do pulo, pequena e mais lenta."""
    def __init__(self,x,y,speed):
        self.x=float(x); self.y=float(y); self.speed=speed; self.alive=True
    def update(self): self.x-=self.speed; self.alive=self.x>-BOLINHA_W-10
    def rect(self): m=1; return pygame.Rect(int(self.x)+m,int(self.y)+m,BOLINHA_W-m*2,BOLINHA_H-m*2)
    def draw(self,surf): surf.blit(bolinha_sprite,(int(self.x),int(self.y)))

class PlayerBullet:
    def __init__(self,x,y,d):
        self.x=float(x); self.y=float(y); self.dir=d; self.alive=True
        # dir= 1 → vai para direita (tiro normal)
        # dir=-1 → vai para esquerda (tiro espelhado)
        self.spr = tiro_sprite if d == 1 else tiro_sprite_flip
    def update(self): self.x+=12*self.dir; self.alive=-50<self.x<WIDTH+50
    def rect(self): return pygame.Rect(int(self.x),int(self.y),PBULLET_W,PBULLET_H)
    def draw(self,surf): surf.blit(self.spr,(int(self.x),int(self.y)))

class Particle:
    def __init__(self,x,y,color):
        self.x=float(x); self.y=float(y)
        self.vx=random.uniform(-4,4); self.vy=random.uniform(-6,-1)
        self.life=random.randint(20,40); self.color=color; self.r=random.randint(3,8)
    def update(self): self.x+=self.vx; self.y+=self.vy; self.vy+=0.3; self.life-=1
    def draw(self,surf):
        if self.life>0:
            pygame.draw.circle(surf,self.color,(int(self.x),int(self.y)),max(1,int(self.r*self.life/40)))

# ===== Cauda (Fase 1) — varre o céu, desce quando alinhada com o jogador =====
class JacareHead:
    """
    Ciclo:
    'sweeping' — ~40% do sprite visível no topo, move lado a lado.
                Desce IMEDIATAMENTE quando alinhada com o jogador,
                desde que o cooldown de 2s entre descidas tenha passado.
    'falling'  — desce
    'holding'  — pausa curta no chão
    'rising'   — sobe de volta → retorna a 'sweeping'
    """
    SWEEP_SPEED    = 5      # px/frame varrendo
    FALL_SPEED     = 13     # px/frame caindo
    RISE_SPEED     = 20     # px/frame subindo
    HOLD_TIME      = 25     # frames no chão
    MIN_DIVE_DELAY = 120    # frames de cooldown entre descidas (2s a 60fps)
    ALIGN_MARGIN   = 50     # px de tolerância para considerar "alinhado"
    PEEK_Y         = -JLADO_H + int(JLADO_H * 0.40)

    def __init__(self):
        self.state         = 'idle'
        self.x             = 0.0
        self.y             = float(self.PEEK_Y)
        self.sweep_dir     = 1
        self.timer         = 0
        self.dive_cooldown = 0
        self.done          = False

    def start(self, player_x):
        self.x             = float(random.randint(0, max(0, WIDTH - JLADO_W)))
        self.y             = float(self.PEEK_Y)
        self.sweep_dir     = random.choice([-1, 1])
        self.timer         = 0
        self.dive_cooldown = self.MIN_DIVE_DELAY  # espera inicial antes da 1ª descida
        self.done          = False
        self.state         = 'sweeping'

    def update(self, player_x):
        if self.state == 'idle':
            return

        self.timer += 1
        if self.dive_cooldown > 0:
            self.dive_cooldown -= 1

        if self.state == 'sweeping':
            self.x += self.SWEEP_SPEED * self.sweep_dir
            if self.x <= 0:
                self.x = 0.0; self.sweep_dir = 1
            if self.x >= WIDTH - JLADO_W:
                self.x = float(WIDTH - JLADO_W); self.sweep_dir = -1

            # Desce imediatamente ao passar sobre o jogador, se cooldown zerado
            cauda_cx  = self.x + JLADO_W / 2
            player_cx = player_x + PLAYER_W / 2
            if self.dive_cooldown == 0 and abs(cauda_cx - player_cx) <= self.ALIGN_MARGIN:
                self.state = 'falling'
                self.timer = 0

        elif self.state == 'falling':
            self.y += self.FALL_SPEED
            if self.y + JLADO_H >= GROUND_Y:
                self.y     = float(GROUND_Y - JLADO_H)
                self.state = 'holding'
                self.timer = 0

        elif self.state == 'holding':
            if self.timer >= self.HOLD_TIME:
                self.state         = 'rising'
                self.dive_cooldown = self.MIN_DIVE_DELAY
                self.timer         = 0

        elif self.state == 'rising':
            self.y -= self.RISE_SPEED
            if self.y <= self.PEEK_Y:
                self.y     = float(self.PEEK_Y)
                self.state = 'sweeping'
                self.timer = 0
                self.done  = True

    def rect(self):
        if self.state in ('falling', 'holding'):
            tip_h    = JLADO_H // 4
            margin_x = JLADO_W // 3
            return pygame.Rect(
                int(self.x) + margin_x,
                int(self.y) + JLADO_H - tip_h,
                JLADO_W - margin_x * 2,
                tip_h
            )
        return pygame.Rect(0, 0, 0, 0)

    def draw_bg(self, surf):
        if self.state != 'idle':
            surf.blit(jacarelado_sprite, (int(self.x), int(self.y)))

# ===== Player =====
class Player_2:
    def __init__(self): self.reset()
    def reset(self):
        self.x=80.0; self.y=float(GROUND_Y-PLAYER_H)
        self.vx=0.0; self.vy=0.0; self.on_ground=False
        self.facing=1; self.hp=PLAYER_HP_MAX
        self.inv_timer=0; self.shoot_cd=0; self.shooting=False
    def update(self, keys):
        self.vx=0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.vx=-PLAYER_SPEED; self.facing=-1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx= PLAYER_SPEED; self.facing= 1
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vy=PLAYER_JUMP_V; self.on_ground=False
        self.vy+=GRAVITY_2; self.x+=self.vx; self.y+=self.vy
        if self.y>=GROUND_Y-PLAYER_H: self.y=GROUND_Y-PLAYER_H; self.vy=0; self.on_ground=True
        # Limites laterais — parede invisível à direita impedindo chegar ao boss
        self.x = max(0, min(PLATFORM_X - PLAYER_W - 5, self.x))
        if self.inv_timer>0: self.inv_timer-=1
        if self.shoot_cd>0:  self.shoot_cd-=1
        self.shooting=keys[pygame.K_z] or keys[pygame.K_LCTRL]
    def shoot(self):
        if self.shoot_cd==0 and self.shooting:
            self.shoot_cd=12
            bx = self.x+PLAYER_W if self.facing==1 else self.x-PBULLET_W
            by = self.y+PLAYER_H//2-PBULLET_H//2
            return PlayerBullet(bx,by,self.facing)
        return None
    def take_hit(self):
        if self.inv_timer==0: self.hp-=1; self.inv_timer=90; return True
        return False
    def rect(self): return pygame.Rect(int(self.x)+8,int(self.y)+10,PLAYER_W-16,PLAYER_H-14)
    def draw(self,surf):
        if self.inv_timer>0 and (self.inv_timer//6)%2==1: return
        draw_player(surf, self.x, self.y, self.facing, self.hp, self.shooting,
                    jumping=not self.on_ground)

# ===== Boss =====
class Boss:
    def __init__(self): self.reset()
    def reset(self):
        self.hp=BOSS_HP_MAX; self.inv_timer=0; self.attacking=False
    def phase(self):
        if self.hp > PHASE2_HP: return 1
        if self.hp > PHASE3_HP: return 2
        return 3
    def rect(self): return pygame.Rect(BOSS_X+BOSS_W//4,BOSS_Y+BOSS_H//4,BOSS_W//2,BOSS_H//2)
    def take_hit(self):
        if self.inv_timer==0: self.hp=max(0,self.hp-1); self.inv_timer=20; return True
        return False
    def update(self):
        if self.inv_timer>0: self.inv_timer-=1
    def draw(self,surf,tick): draw_boss_sprite(surf,self.hp,self.attacking,tick)

# ===== Gerenciador de fases =====
class PhaseManager:
    P1_ATTACK_INTERVAL  = 80    # delay inicial antes da primeira cauda
    P2_SPAWN_INTERVAL   = 62    # frames entre spawns fase 2 (reduzido)
    P3_HORIZ_INTERVAL   = 70    # frames entre mísseis fase 3 (era 55, menos frequente)
    P3_HORIZ_GAP        = 280
    P3_BOLINHA_INTERVAL = 120

    def __init__(self): self.reset()

    def reset(self):
        self.phase       = 1
        self.transition  = False
        self.trans_timer = 0
        self.TRANS_DUR   = 90
        # Fase 1
        self.jacare_head = JacareHead()
        self.head_timer  = 80    # delay inicial antes da primeira cabeçada
        self.head_active = False
        # Fase 2
        self.p2_timer = 0
        # Fase 3
        self.p3_horiz_timer   = 0
        self.p3_bolinha_timer = 0

    def update(self, boss, fall_bullets, horiz_missiles, diag_missiles,
            bolinhas, player, particles):
        """Retorna True se o jogador morreu."""

        # ── Pausa de transição entre fases ───────────────────────────────
        if self.transition:
            self.trans_timer += 1
            if self.trans_timer >= self.TRANS_DUR:
                self.transition  = False
                self.trans_timer = 0
                self.head_timer  = 60
                self.p2_timer    = 0
                self.p3_horiz_timer   = 0
                self.p3_bolinha_timer = 0
            return False

        current = boss.phase()

        # ── Detecta mudança de fase ───────────────────────────────────────
        if current != self.phase:
            self.phase      = current
            self.transition = True
            self.trans_timer = 0
            fall_bullets.clear(); horiz_missiles.clear()
            diag_missiles.clear(); bolinhas.clear()
            self.jacare_head.state = 'idle'
            return False

        # ── FASE 1: cauda do céu ─────────────────────────────────────────
        if self.phase == 1:
            boss.attacking = self.jacare_head.state in ('falling', 'holding')
            self.jacare_head.update(player.x)

            # Inicia o primeiro ciclo após o delay inicial
            if self.jacare_head.state == 'idle' and self.head_timer > 0:
                self.head_timer -= 1
                if self.head_timer == 0:
                    self.jacare_head.start(player.x)

            # done=True significa que completou 1 ciclo — atualiza o target_x
            # mas a cauda já voltou ao sweeping sozinha, não precisa reiniciar
            if self.jacare_head.done:
                self.jacare_head.done = False

            # Colisão cauda x jogador (só quando está descendo ou parada)
            if self.jacare_head.state in ('falling', 'holding'):
                if self.jacare_head.rect().colliderect(player.rect()):
                    if player.take_hit():
                        for _ in range(12):
                            particles.append(Particle(
                                player.x+PLAYER_W//2, player.y+PLAYER_H//2, C_RED))
                        if player.hp<=0: return True

        # ── FASE 2: chuva contínua — verticais + diagonais ───────────────
        elif self.phase == 2:
            boss.attacking = True
            self.p2_timer += 1
            if self.p2_timer >= self.P2_SPAWN_INTERVAL:
                self.p2_timer = 0
                fall_bullets.extend(spawn_rain(3, 1.5))   # era 4
                if random.random() < 0.4:                  # era 0.5
                    diag_missiles.extend(spawn_diag(2, 1.5))

        # ── FASE 3: mísseis rasteiros + bolinhas na altura do pulo ───────
        elif self.phase == 3:
            boss.attacking = True

            # Mísseis horizontais RASTEIROS — 1 por vez, mais rápidos
            self.p3_horiz_timer += 1
            if self.p3_horiz_timer >= self.P3_HORIZ_INTERVAL:
                self.p3_horiz_timer = 0
                hy = random.randint(P3_HORIZ_Y_MIN, P3_HORIZ_Y_MAX)
                # Velocidade 1.8x maior que a base
                horiz_missiles.append(HorizontalMissile(WIDTH, hy, HORIZ_SPD * 1.8))

            # Bolinhas — menos frequentes, pequenas, na altura do pulo
            self.p3_bolinha_timer += 1
            if self.p3_bolinha_timer >= self.P3_BOLINHA_INTERVAL:
                self.p3_bolinha_timer = 0
                jump_y = GROUND_Y - PLAYER_H - random.randint(50, 120)
                bolinhas.append(Bolinha(WIDTH+10, jump_y, HORIZ_SPD * 0.45))

        return False

    def draw_bg(self, surf, tick):
        """Camada de fundo: cauda (antes da HUD)."""
        if self.phase == 1:
            self.jacare_head.draw_bg(surf)

    def draw_fg(self, surf, tick):
        """Camada de frente: banner de transição (após HUD)."""
        if self.transition and (tick//12)%2==0:
            txt = font_med.render("── PRÓXIMA FASE ──", True, C_YELLOW)
            surf.blit(font_med.render("── PRÓXIMA FASE ──",True,C_BLACK),
                    (WIDTH//2-txt.get_width()//2+2, HEIGHT//2-42))
            surf.blit(txt, (WIDTH//2-txt.get_width()//2, HEIGHT//2-44))
