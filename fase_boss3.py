# --- Tela do Boss 3: Rato no Robô
import pygame
from config import *
from classes import Tile, Player, Boss3, player_movement


def draw_boss_hp(surface, boss):
    """Desenha a barra de vida do boss no topo da tela."""
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


def draw_player_hp(surface, player, hp_imgs):
    """Desenha o HUD de vidas no canto inferior esquerdo."""
    if player.hp >= 3:
        img = hp_imgs[3]
    elif player.hp == 2:
        img = hp_imgs[2]
    else:
        img = hp_imgs[1]

    target_h = 48
    orig_w, orig_h = img.get_size()
    scale = target_h / orig_h
    target_w = int(orig_w * scale)
    img_scaled = pygame.transform.scale(img, (target_w, target_h))

    margin = 12
    x = margin
    y = HEIGHT - target_h - margin
    surface.blit(img_scaled, (x, y))


def boss3_screen(window, hp_imgs):
    clock  = pygame.time.Clock()
    assets = load_assets(img_dir)

    # Background redimensionado para a tela
    bg = pygame.transform.scale(assets[BG_BOSS3], (WIDTH, 659))

    # --- Grupos de sprites
    all_sprites       = pygame.sprite.Group()
    platforms         = pygame.sprite.Group()
    blocks            = pygame.sprite.Group()
    floor_group       = pygame.sprite.Group()
    all_bullets       = pygame.sprite.Group()
    enemy_projectiles = pygame.sprite.Group()
    mines_group       = pygame.sprite.Group()

    # --- all_groups definido ANTES do loop do mapa
    all_groups = {
        'all_sprites': all_sprites,
        'platforms':   platforms,
        'blocks':      blocks,
        'all_bullets': all_bullets,
        'all_enemies': pygame.sprite.Group(),
    }

    # --- Mapa
    for row in range(len(MAP3)):
        for col in range(len(MAP3[row])):
            tile_type = MAP3[row][col]
            if tile_type != EMPTY:
                img = None if tile_type == INVIS else assets[tile_type]
                tile = Tile(img, row, col)
                all_sprites.add(tile)
                if tile_type == BLOCK:
                    blocks.add(tile)
                elif tile_type in (PLATF, INVIS):
                    platforms.add(tile)
                    if row == 13:
                        floor_group.add(tile)

    # --- Player
    player = Player(assets[PLAYER_IMG], 11, 2, assets, all_groups)
    player.hp        = PLAYER_HP
    player.jump_size = JUMP_SIZE_BOSS3          # pulo mais alto nessa fase
    player.floor_y   = 13 * TILE_SIZE           # não desce abaixo do chão visual
    all_sprites.add(player)

    # --- Controle de dano do player (i-frames manual para boss3)
    I_FRAMES_BOSS3  = 1500
    last_player_hit = -I_FRAMES_BOSS3

    # --- Boss
    boss = Boss3(
        assets[BOSS_IMG],
        assets[BOSS_WALK_IMG],
        assets[BOSS_NAIL_IMG],
        assets[BOSS_WRENCH_IMG],
        assets[BOSS_DEAD_IMG],
        assets[BOSS_GEAR_IMG],
        WIDTH - BOSS3_WIDTH - 30,
        13 * TILE_SIZE,
        blocks, floor_group,
        assets[NAIL_IMG], assets[GEAR_IMG], assets[MINE_IMG],
        assets[EXPLOSION_IMG], assets[WRENCH_SLASH_IMG],
        enemy_projectiles, mines_group, all_sprites
    )
    all_sprites.add(boss)
    boss.player_ref = player

    font_big = pygame.font.SysFont(None, 80)
    state    = BOSS3

    def player_take_damage():
        """Aplica 1 de dano ao player respeitando i-frames."""
        nonlocal last_player_hit
        now = pygame.time.get_ticks()
        if now - last_player_hit >= I_FRAMES_BOSS3 and player.alive:
            player.hp -= 1
            last_player_hit = now
            player.invincible = True
            if player.hp <= 0:
                player.alive = False
                player.speedx = 0
            return True
        return False

    while state == BOSS3:
        clock.tick(FPS)

        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = QUIT
            player_movement(player, event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    state = INIT

        # Efeito de piscar durante invulnerabilidade
        if player.invincible:
            if now - last_player_hit > I_FRAMES_BOSS3:
                player.invincible = False
                player.image.set_alpha(255)
            else:
                import math
                alpha = int(100 * abs(math.sin(now * (25/1000))) + 155)
                player.image.set_alpha(alpha)
        else:
            player.image.set_alpha(255)

        all_sprites.update()

        # --- Colisões de dano ao player ---
        proj_hits = pygame.sprite.spritecollide(player, enemy_projectiles, True)
        if proj_hits:
            if player_take_damage():
                player.speedy = -8

        wrench_rect = boss.get_wrench_rect()
        if wrench_rect and player.rect.colliderect(wrench_rect):
            if player_take_damage():
                player.speedy  = -10
                player.rect.x += 60 * boss.direction

        mine_player_hits = pygame.sprite.spritecollide(player, mines_group, False)
        for mine in mine_player_hits:
            mine.explode()
            if player_take_damage():
                player.speedy = -8

        # --- Colisões de dano ao boss ---
        hits = pygame.sprite.spritecollide(boss, all_bullets, True)
        for _ in hits:
            boss.take_damage(1)

        mine_bullet_hits = pygame.sprite.groupcollide(mines_group, all_bullets, False, True)
        for mine in mine_bullet_hits:
            mine.explode()

        # --- Desenho ---
        window.fill((30, 25, 20))
        window.blit(bg, (0, 0))
        window.set_clip((0, 0, WIDTH, 659))
        all_sprites.draw(window)
        window.set_clip(None)

        if wrench_rect:
            slash_img = boss.get_wrench_slash_img()
            if slash_img is not None:
                window.blit(slash_img, wrench_rect.topleft)

        if boss.alive:
            draw_boss_hp(window, boss)

        draw_player_hp(window, player, hp_imgs)

        if not boss.alive:
            txt = font_big.render('CHEFÃO DERROTADO!', True, (255, 220, 50))
            window.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 40))
            pygame.display.flip()
            pygame.time.wait(3000)
            state = INIT

        if not player.alive:
            txt = font_big.render('VOCÊ MORREU!', True, (220, 50, 50))
            window.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 40))
            pygame.display.flip()
            pygame.time.wait(2000)
            state = INIT

        pygame.display.flip()

    return state