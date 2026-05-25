# ===== Cuphead-style Boss Fight =====
import pygame, random, math, json, base64, io
pygame.init()

WIDTH, HEIGHT, FPS = 1080, 720, 60
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cuphead Boss Fight")
clock = pygame.time.Clock()

font_large = pygame.font.SysFont("Arial", 64, bold=True)
font_med   = pygame.font.SysFont("Arial", 36, bold=True)
font_small = pygame.font.SysFont("Arial", 24)

# ===== Paleta =====
C_BG_SKY    = (255, 200, 100)
C_BG_GROUND = (120, 80,  40)
C_BG_GRASS  = (60,  160, 60)
C_BLACK     = (10,  10,  10)
C_WHITE     = (255, 255, 255)
C_RED       = (220, 50,  50)
C_DARK_RED  = (140, 20,  20)
C_YELLOW    = (255, 220, 0)
C_ORANGE    = (255, 130, 0)
C_DARK_GRAY = (60,  60,  60)
C_GREEN     = (40,  180, 80)
C_OUTLINE   = (10,  10,  10)

# ===== Constantes =====
GROUND_Y           = HEIGHT - 120
PLAYER_SPEED       = 5
PLAYER_JUMP_V      = -16
GRAVITY            = 0.7
PLAYER_W           = 52
PLAYER_H           = 68
BOSS_HP_MAX        = 90
PLAYER_HP_MAX      = 3

BOSS_ATTACK_INTERVAL  = 300
BOSS_RAIN_DURATION    = 240
BOSS_BULLETS_PER_RAIN = 18

BASE_FALL_SPEED_MIN = 3.5
BASE_FALL_SPEED_MAX = 6.5
HORIZ_SPEED_BASE    = 5.0

# Largura mínima garantida de corredor livre entre mísseis (em px)
# Garante que o jogador (PLAYER_W=52) sempre tenha por onde passar
MIN_GAP = PLAYER_W + 40   # 92px de folga

def horde_speed_mult(horde):
    return 1.0 + (min(horde, 7) - 1) / 6.0


# ===== Carrega sprites do Pixilart =====
def load_pixil_surface(path):
    import PIL.Image
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    src  = data["frames"][0]["layers"][0]["src"]
    b64  = src.split(",", 1)[1]
    buf  = io.BytesIO(base64.b64decode(b64))
    img  = PIL.Image.open(buf).convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    return pygame.image.frombytes(img.tobytes(), img.size, "RGBA").convert_alpha()

_boss_raw   = load_pixil_surface("jacare.pixil")   # 67x62 px
_missil_raw = load_pixil_surface("míssil.pixil")   # 19x38 px  fogo=y0, bico=y37

# Jacaré: escala 4x → 268x248 px
BOSS_SCALE  = 4
boss_sprite = pygame.transform.scale(
    _boss_raw,
    (_boss_raw.get_width() * BOSS_SCALE, _boss_raw.get_height() * BOSS_SCALE)
)
BOSS_W = boss_sprite.get_width()
BOSS_H = boss_sprite.get_height()

# Rostos do boss — escala 3x, exibidos acima da barra de HP
# rosto1: hp entre 100% e 2/3  (normal)
# rosto2: hp entre 2/3  e 1/3  (irritado)
# rosto3: hp entre 1/3  e 0    (furioso)
FACE_SCALE = 3
_face_raws = [
    load_pixil_surface("rosto_jacare1.pixil"),
    load_pixil_surface("rosto_jacare_3.pixil"),
    load_pixil_surface("rosto_jacare_4.pixil"),
]
boss_faces = [
    pygame.transform.scale(r, (r.get_width() * FACE_SCALE, r.get_height() * FACE_SCALE))
    for r in _face_raws
]

# ── Míssil caindo ──────────────────────────────────────────────────────────────
# Sprite original: fogo no y=0 (topo), bico no y=37 (base) → JÁ está correto
# para cair do céu com bico apontando para baixo. SEM nenhuma rotação.
# Escala 2x → 38x76. Depois redimensionamos só a LARGURA para 50% (19x76)
# para ficar bem fino, mantendo a altura.
_mf_2x = pygame.transform.scale(
    _missil_raw,
    (_missil_raw.get_width() * 2, _missil_raw.get_height() * 2)   # 38x76
)
# Afina: mantém altura, reduz largura à metade → 19x76 px (muito fino)
missil_fall_sprite = pygame.transform.scale(_mf_2x, (19, 76))
BULLET_W = missil_fall_sprite.get_width()    # 19
BULLET_H = missil_fall_sprite.get_height()   # 76

# ── Míssil horizontal ──────────────────────────────────────────────────────────
# Partindo do sprite original (fogo↑ bico↓), rotacionamos 90° horário:
# fogo fica à direita, bico à esquerda → correto para ir da direita para esquerda
_mh_2x = pygame.transform.scale(
    _missil_raw,
    (_missil_raw.get_width() * 2, _missil_raw.get_height() * 2)
)
missil_horiz_sprite = pygame.transform.rotate(_mh_2x, 90)   # bico←, fogo→
HORIZ_W = missil_horiz_sprite.get_width()
HORIZ_H = missil_horiz_sprite.get_height()

PLAYER_BULLET_W, PLAYER_BULLET_H = 16, 8
_player_bullet_surf = pygame.Surface((PLAYER_BULLET_W, PLAYER_BULLET_H), pygame.SRCALPHA)
pygame.draw.ellipse(_player_bullet_surf, C_YELLOW, (0,0,PLAYER_BULLET_W,PLAYER_BULLET_H))
pygame.draw.ellipse(_player_bullet_surf, C_WHITE,  (2,1,6,4))

# Plataforma e posição do boss
PLATFORM_X = WIDTH - BOSS_W - 20
PLATFORM_W = BOSS_W + 40
PLATFORM_H = 24
PLATFORM_Y = GROUND_Y - PLATFORM_H
BOSS_X     = PLATFORM_X - 20
BOSS_Y     = PLATFORM_Y - BOSS_H + 10


# ===== Gerador de chuva com escapatória garantida =========================
def spawn_rain_safe(n_bullets, mult):
    """
    Distribui N mísseis pelo eixo X garantindo pelo menos UM corredor
    de MIN_GAP pixels onde o jogador pode ficar em segurança.
    """
    lo = BASE_FALL_SPEED_MIN * mult
    hi = BASE_FALL_SPEED_MAX * mult

    usable_w = WIDTH - 40          # margem de 20px em cada lado
    gap_w    = MIN_GAP             # corredor livre garantido

    # Escolhe posição aleatória para o corredor livre
    gap_start = random.randint(20, usable_w - gap_w)
    gap_end   = gap_start + gap_w

    # Divide o espaço disponível em segmentos fora do corredor
    left_zone  = (20,         gap_start - BULLET_W)
    right_zone = (gap_end,    usable_w - BULLET_W)

    bullets = []
    for _ in range(n_bullets):
        # Sorteia em qual zona vai este míssil
        zones = []
        if left_zone[1] > left_zone[0]:   zones.append(left_zone)
        if right_zone[1] > right_zone[0]: zones.append(right_zone)

        if zones:
            z = random.choice(zones)
            bx = random.randint(z[0], z[1])
        else:
            # fallback: qualquer posição fora do corredor
            bx = random.randint(20, usable_w - BULLET_W)

        by  = random.randint(-400, -BULLET_H)
        spd = random.uniform(lo, hi)
        bullets.append(FallingBullet(bx, by, spd))

    return bullets, gap_start, gap_end   # retorna também o corredor para debug opcional


# ===== Cenário =====
def draw_outlined_circle(surf, color, center, radius, outline=3):
    pygame.draw.circle(surf, C_OUTLINE, center, radius + outline)
    pygame.draw.circle(surf, color,     center, radius)

def draw_cloud(surf, cx, cy, scale):
    br = int(40 * scale)
    pygame.draw.circle(surf, C_OUTLINE, (cx, cy), br+2)
    pygame.draw.circle(surf, C_WHITE,   (cx, cy), br)
    for dx,dy,r in [(-35,10,28),(35,10,28),(0,18,32)]:
        rx,ry,rr = int(cx+dx*scale),int(cy+dy*scale),int(r*scale)
        pygame.draw.circle(surf, C_OUTLINE, (rx,ry), rr+2)
        pygame.draw.circle(surf, C_WHITE,   (rx,ry), rr)

def draw_background(surf, tick):
    for y in range(GROUND_Y):
        t = y / GROUND_Y
        pygame.draw.line(surf,
            (int(C_BG_SKY[0]*(1-t)+200*t),
             int(C_BG_SKY[1]*(1-t)+170*t),
             int(100*(1-t)+80*t)),
            (0,y),(WIDTH,y))
    for cx,cy,sp,sc in [(200,80,.3,1.0),(500,50,.2,1.3),(800,100,.4,.8),(100,130,.15,1.1)]:
        draw_cloud(surf, int((cx+tick*sp)%(WIDTH+200))-100, cy, sc)
    pygame.draw.rect(surf, C_BG_GRASS,  (0, GROUND_Y-20, WIDTH, 28))
    pygame.draw.rect(surf, C_BG_GROUND, (0, GROUND_Y+8,  WIDTH, HEIGHT))
    for x in range(0, WIDTH, 60):
        pygame.draw.rect(surf, (100,65,30), (x, GROUND_Y+8, 30, 10))
    # Relevo do boss
    pygame.draw.rect(surf, (160,110,60),
                     (PLATFORM_X-20, PLATFORM_Y, PLATFORM_W+40, HEIGHT-PLATFORM_Y),
                     border_radius=6)
    pygame.draw.rect(surf, C_OUTLINE,
                     (PLATFORM_X-20, PLATFORM_Y, PLATFORM_W+40, HEIGHT-PLATFORM_Y),
                     3, border_radius=6)
    pygame.draw.rect(surf, C_BG_GRASS,
                     (PLATFORM_X-24, PLATFORM_Y-12, PLATFORM_W+48, 18),
                     border_radius=5)
    pygame.draw.rect(surf, C_OUTLINE,
                     (PLATFORM_X-24, PLATFORM_Y-12, PLATFORM_W+48, 18),
                     3, border_radius=5)

def draw_player(surf, x, y, facing, hp, shooting):
    cx = int(x + PLAYER_W//2)
    leg_y = int(y + PLAYER_H - 8)
    pygame.draw.rect(surf, C_BLACK,    (cx-18,leg_y-20,12,24))
    pygame.draw.rect(surf, C_BLACK,    (cx+6, leg_y-20,12,24))
    pygame.draw.ellipse(surf, C_BLACK, (cx-24,leg_y,20,12))
    pygame.draw.ellipse(surf, C_BLACK, (cx+4, leg_y,20,12))
    body = pygame.Rect(cx-22,int(y+28),44,32)
    pygame.draw.ellipse(surf, C_OUTLINE, body.inflate(4,4))
    pygame.draw.ellipse(surf, C_WHITE,   body)
    for i in range(3):
        lx = body.x+6+i*12
        pygame.draw.line(surf, C_RED,(lx,body.top+4),(lx,body.bottom-4),3)
    hx = cx+(1 if facing==1 else -1)*24
    pygame.draw.arc(surf, C_OUTLINE,(hx-10,int(y+32),20,20),math.pi*.5,math.pi*1.5,4)
    pygame.draw.rect(surf, C_OUTLINE,(cx-5,int(y+18),10,14))
    pygame.draw.rect(surf,(240,200,170),(cx-4,int(y+19),8,12))
    draw_outlined_circle(surf,(240,200,170),(cx,int(y+14)),20)
    eo = 6*facing
    pygame.draw.circle(surf,C_BLACK,(cx+eo,int(y+12)),5)
    pygame.draw.circle(surf,C_WHITE,(cx+eo+1,int(y+11)),2)
    mx = cx+eo
    if shooting: pygame.draw.circle(surf,C_DARK_RED,(mx,int(y+20)),4)
    else: pygame.draw.arc(surf,C_DARK_RED,(mx-5,int(y+16),10,8),math.pi,2*math.pi,2)
    pygame.draw.rect(surf,C_OUTLINE,(cx-3,int(y-10),6,16))
    pygame.draw.rect(surf,C_RED,    (cx-2,int(y-9), 4,14))
    for i in range(hp):
        draw_heart(surf,int(x)+i*14,int(y)-24,8)

def draw_heart(surf,x,y,size):
    pygame.draw.circle(surf,C_RED,(x+size//2,y+size//2),size//2)
    pygame.draw.circle(surf,C_RED,(x+size,   y+size//2),size//2)
    pygame.draw.polygon(surf,C_RED,[(x,y+size//2),(x+size,y+size+size//2),(x+size*2,y+size//2)])

def draw_boss_sprite(surf, hp, attacking, tick):
    bob = int(math.sin(tick*0.04)*4) if attacking else 0
    surf.blit(boss_sprite, (BOSS_X, BOSS_Y+bob))
    if attacking and (tick//8)%2==0:
        glow = pygame.Surface((BOSS_W,BOSS_H), pygame.SRCALPHA)
        pygame.draw.circle(glow,(255,220,0,70),(BOSS_W//2,BOSS_H//3),28)
        surf.blit(glow,(BOSS_X, BOSS_Y+bob))

    # ── Rosto acima da barra de HP ──────────────────────────────────────────
    # Seleciona o rosto conforme a faixa de vida
    if   hp > BOSS_HP_MAX * 2/3: face = boss_faces[0]   # 100% – 67%  normal
    elif hp > BOSS_HP_MAX * 1/3: face = boss_faces[1]   #  67% – 34%  irritado
    else:                         face = boss_faces[2]   #  33% –  0%  furioso

    # Barra de HP
    bw=300; bx=WIDTH//2-bw//2; by=56          # by desceu para dar espaço ao rosto
    pygame.draw.rect(surf,C_OUTLINE,  (bx-2,by-2,bw+4,24))
    pygame.draw.rect(surf,C_DARK_GRAY,(bx,by,bw,20))
    hw=int(bw*hp/BOSS_HP_MAX)
    if hw>0:
        hc=C_GREEN if hp>BOSS_HP_MAX*2/3 else C_YELLOW if hp>BOSS_HP_MAX*1/3 else C_RED
        pygame.draw.rect(surf,hc,(bx,by,hw,20),border_radius=2)

    # Rosto centralizado acima da barra
    face_x = WIDTH//2 - face.get_width()//2
    face_y = by - face.get_height() - 4
    surf.blit(face, (face_x, face_y))

def draw_hud(surf, score, horde):
    surf.blit(font_med.render(f"SCORE: {score}",True,C_BLACK),(22,52))
    surf.blit(font_med.render(f"SCORE: {score}",True,C_WHITE),(20,50))
    surf.blit(font_small.render(f"Horda: {horde}",True,C_BLACK),(22,92))
    surf.blit(font_small.render(f"Horda: {horde}",True,C_YELLOW),(20,90))

def draw_warning(surf, tick):
    if (tick//15)%2==0:
        txt=font_med.render("⚠ CUIDADO! ⚠",True,C_RED)
        surf.blit(font_med.render("⚠ CUIDADO! ⚠",True,C_BLACK),(WIDTH//2-txt.get_width()//2+2,HEIGHT//2-52))
        surf.blit(txt,(WIDTH//2-txt.get_width()//2,HEIGHT//2-54))

def draw_game_over(surf, win):
    ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((0,0,0,160)); surf.blit(ov,(0,0))
    msg="VOCÊ VENCEU!" if win else "GAME OVER"
    txt=font_large.render(msg,True,C_YELLOW if win else C_RED)
    surf.blit(font_large.render(msg,True,C_BLACK),(WIDTH//2-txt.get_width()//2+4,HEIGHT//2-44))
    surf.blit(txt,(WIDTH//2-txt.get_width()//2,HEIGHT//2-48))
    sub=font_small.render("R = recomeçar  |  ESC = sair",True,C_WHITE)
    surf.blit(sub,(WIDTH//2-sub.get_width()//2,HEIGHT//2+20))


# ===== Classes =====
class Player:
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
        self.vy+=GRAVITY; self.x+=self.vx; self.y+=self.vy
        if self.y>=GROUND_Y-PLAYER_H: self.y=GROUND_Y-PLAYER_H; self.vy=0; self.on_ground=True
        self.x=max(0,min(WIDTH-PLAYER_W,self.x))
        if self.inv_timer>0: self.inv_timer-=1
        if self.shoot_cd>0:  self.shoot_cd-=1
        self.shooting=keys[pygame.K_z] or keys[pygame.K_LCTRL]
    def shoot(self):
        if self.shoot_cd==0 and self.shooting:
            self.shoot_cd=12
            bx=self.x+PLAYER_W if self.facing==1 else self.x-PLAYER_BULLET_W
            by=self.y+PLAYER_H//2-PLAYER_BULLET_H//2
            return PlayerBullet(bx,by,self.facing)
        return None
    def take_hit(self):
        if self.inv_timer==0: self.hp-=1; self.inv_timer=90; return True
        return False
    def rect(self): return pygame.Rect(int(self.x)+8,int(self.y)+10,PLAYER_W-16,PLAYER_H-14)
    def draw(self, surf):
        if self.inv_timer>0 and (self.inv_timer//6)%2==1: return
        draw_player(surf,self.x,self.y,self.facing,self.hp,self.shooting)


class Boss:
    def __init__(self): self.reset()
    def reset(self):
        self.hp=BOSS_HP_MAX; self.attack_timer=BOSS_ATTACK_INTERVAL
        self.rain_timer=0; self.attacking=False; self.inv_timer=0; self.horde=1
    def rect(self):
        return pygame.Rect(BOSS_X+BOSS_W//4, BOSS_Y+BOSS_H//4, BOSS_W//2, BOSS_H//2)
    def take_hit(self):
        if self.inv_timer==0: self.hp-=1; self.inv_timer=20; return True
        return False
    def update(self):
        if self.inv_timer>0: self.inv_timer-=1
        if self.rain_timer>0:
            self.rain_timer-=1; self.attacking=True; return [],None
        self.attacking=False; self.attack_timer-=1
        if self.attack_timer<=0:
            self.attack_timer=BOSS_ATTACK_INTERVAL
            self.rain_timer=BOSS_RAIN_DURATION
            self.horde+=1
            mult=horde_speed_mult(self.horde)
            falls,_,_ = spawn_rain_safe(BOSS_BULLETS_PER_RAIN, mult)
            horiz=self._spawn_horiz(mult) if self.horde>=5 else None
            return falls, horiz
        return [], None
    def _spawn_horiz(self, mult):
        hy=random.randint(GROUND_Y-PLAYER_H-10, GROUND_Y-PLAYER_H//2)
        return HorizontalMissile(WIDTH, hy, HORIZ_SPEED_BASE*mult)
    def draw(self, surf, tick):
        draw_boss_sprite(surf, self.hp, self.attacking, tick)


class FallingBullet:
    def __init__(self,x,y,speed):
        self.x=float(x); self.y=float(y); self.speed=speed; self.alive=True
    def update(self):
        self.y+=self.speed
        if self.y>HEIGHT: self.alive=False
    def rect(self):
        # hitbox estreita proporcional ao sprite fino
        m=3
        return pygame.Rect(int(self.x)+m, int(self.y)+m, BULLET_W-m*2, BULLET_H-m*2)
    def draw(self, surf):
        # sem rotação — fogo em cima, bico em baixo, cai reto
        surf.blit(missil_fall_sprite,(int(self.x),int(self.y)))


class HorizontalMissile:
    def __init__(self,x,y,speed):
        self.x=float(x); self.y=float(y); self.speed=speed; self.alive=True
    def update(self):
        self.x-=self.speed
        if self.x<-HORIZ_W-20: self.alive=False
    def rect(self):
        m=4
        return pygame.Rect(int(self.x)+m,int(self.y)+m,HORIZ_W-m*2,HORIZ_H-m*2)
    def draw(self, surf):
        surf.blit(missil_horiz_sprite,(int(self.x),int(self.y)))


class PlayerBullet:
    def __init__(self,x,y,direction):
        self.x=float(x); self.y=float(y); self.dir=direction; self.speed=12; self.alive=True
    def update(self):
        self.x+=self.speed*self.dir
        if self.x<-50 or self.x>WIDTH+50: self.alive=False
    def rect(self): return pygame.Rect(int(self.x),int(self.y),PLAYER_BULLET_W,PLAYER_BULLET_H)
    def draw(self,surf): surf.blit(_player_bullet_surf,(int(self.x),int(self.y)))


class Particle:
    def __init__(self,x,y,color):
        self.x=float(x); self.y=float(y)
        self.vx=random.uniform(-4,4); self.vy=random.uniform(-6,-1)
        self.life=random.randint(20,40); self.color=color; self.r=random.randint(3,8)
    def update(self): self.x+=self.vx; self.y+=self.vy; self.vy+=0.3; self.life-=1
    def draw(self,surf):
        if self.life>0:
            pygame.draw.circle(surf,self.color,(int(self.x),int(self.y)),max(1,int(self.r*self.life/40)))


# ===== Main =====
def reset_game():
    return Player(),Boss(),[],[],[],[],0,0,False,False

def main():
    player,boss,fall_bullets,horiz_missiles,player_bullets,particles,score,tick,game_over,win=reset_game()
    running=True
    # guarda o corredor atual para spawns extras durante a chuva
    current_gap = (0, WIDTH)

    while running:
        clock.tick(FPS)
        keys=pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: running=False
                if event.key==pygame.K_r and game_over:
                    player,boss,fall_bullets,horiz_missiles,player_bullets,particles,score,tick,game_over,win=reset_game()
                    current_gap=(0,WIDTH)

        if not game_over:
            tick+=1
            player.update(keys)
            pb=player.shoot()
            if pb: player_bullets.append(pb)

            new_falls, new_horiz = boss.update()
            if new_falls:
                # boss.update() retornou nova horda — salva o corredor
                # (spawn_rain_safe já foi chamado dentro do boss, mas para os spawns
                #  extras durante a chuva, geramos um corredor coerente)
                _, gs, ge = spawn_rain_safe(0, horde_speed_mult(boss.horde))
                current_gap = (gs, ge)
            fall_bullets.extend(new_falls)
            if new_horiz: horiz_missiles.append(new_horiz)

            # spawns extras durante a chuva — respeitam o mesmo corredor
            if boss.rain_timer>0 and tick%18==0:
                mult=horde_speed_mult(boss.horde)
                lo=BASE_FALL_SPEED_MIN*mult; hi=BASE_FALL_SPEED_MAX*mult
                gs, ge = current_gap
                # sorteia posição fora do corredor
                left_ok  = gs - BULLET_W - 20 > 20
                right_ok = ge + 20 < WIDTH - BULLET_W - 20
                if left_ok and right_ok:
                    if random.random()<0.5:
                        bx=random.randint(20, gs-BULLET_W-4)
                    else:
                        bx=random.randint(ge+4, WIDTH-BULLET_W-20)
                elif left_ok:
                    bx=random.randint(20, gs-BULLET_W-4)
                elif right_ok:
                    bx=random.randint(ge+4, WIDTH-BULLET_W-20)
                else:
                    bx=random.randint(20, WIDTH-BULLET_W-20)
                fall_bullets.append(FallingBullet(bx, random.randint(-180,-BULLET_H), random.uniform(lo,hi)))

            for o in fall_bullets+horiz_missiles+player_bullets+particles: o.update()
            fall_bullets   =[b for b in fall_bullets   if b.alive]
            horiz_missiles =[h for h in horiz_missiles if h.alive]
            player_bullets =[b for b in player_bullets if b.alive]
            particles      =[p for p in particles      if p.life>0]

            prect=player.rect()
            def hit_player(obj):
                nonlocal game_over,win
                if obj.rect().colliderect(prect) and player.take_hit():
                    obj.alive=False
                    for _ in range(12):
                        particles.append(Particle(player.x+PLAYER_W//2,player.y+PLAYER_H//2,C_RED))
                    if player.hp<=0: game_over=True; win=False

            for b in fall_bullets:   hit_player(b)
            for h in horiz_missiles: hit_player(h)

            brect=boss.rect()
            for b in player_bullets:
                if b.rect().colliderect(brect):
                    b.alive=False
                    if boss.take_hit():
                        score+=100
                        for _ in range(10):
                            particles.append(Particle(BOSS_X+BOSS_W//2,BOSS_Y+BOSS_H//2,C_YELLOW))
                        if boss.hp<=0: game_over=True; win=True

        draw_background(window, tick)
        for b in player_bullets: b.draw(window)
        boss.draw(window, tick)
        for b in fall_bullets:   b.draw(window)
        for h in horiz_missiles: h.draw(window)
        player.draw(window)
        for p in particles: p.draw(window)
        draw_hud(window, score, boss.horde)
        if boss.rain_timer>BOSS_RAIN_DURATION-60: draw_warning(window,tick)
        if game_over: draw_game_over(window,win)
        if tick<300 and not game_over:
            lines=["WASD/Setas: mover  |  W/Espaço: pular  |  Z/Ctrl: atirar",
                   "Cada horda fica mais rápida até a 7ª (velocidade dobrada)",
                   "Horda 5+: mísseis horizontais — pule para desviar!"]
            for i,line in enumerate(lines):
                t=font_small.render(line,True,C_BLACK)
                window.blit(t,(WIDTH//2-t.get_width()//2+1,HEIGHT-85+i*22+1))
                window.blit(font_small.render(line,True,C_WHITE),(WIDTH//2-t.get_width()//2,HEIGHT-85+i*22))
        pygame.display.flip()
    pygame.quit()

if __name__=="__main__":
    main()
