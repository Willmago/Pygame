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


def boss3_screen(window):
    clock  = pygame.time.Clock()
    assets = load_boss3_assets(img_dir)

    # Background redimensionado para a tela
    bg = pygame.transform.scale(assets[BG_BOSS3], (WIDTH, 659))

    # --- Grupos de sprites
    all_sprites       = pygame.sprite.Group()
    platforms         = pygame.sprite.Group()
    blocks            = pygame.sprite.Group()
    floor_group       = pygame.sprite.Group()   # só o chão — usado pelo boss
    all_bullets       = pygame.sprite.Group()
    enemy_projectiles = pygame.sprite.Group()
    mines_group       = pygame.sprite.Group()

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
                    # Linha 13 = chão (y=520) vai para floor_group
                    if row == 13:
                        floor_group.add(tile)

    # --- Player
    player = Player(assets[PLAYER_IMG], 11, 2,
                    platforms, blocks, all_bullets, assets, all_sprites)
    all_sprites.add(player)

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
    boss.player_ref = player   # para pregos mirarem no jogador

    font_big = pygame.font.SysFont(None, 80)
    state    = BOSS3

    while state == BOSS3:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state = QUIT
            player_movement(player, event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    state = INIT

        all_sprites.update()

        # Colisão: balas do player × boss
        hits = pygame.sprite.spritecollide(boss, all_bullets, True)
        for _ in hits:
            boss.take_damage(1)

        # Colisão: balas do player × minas — dispara explosão
        mine_bullet_hits = pygame.sprite.groupcollide(mines_group, all_bullets, False, True)
        for mine in mine_bullet_hits:
            mine.explode()

        # Colisão: projéteis do boss × player
        if pygame.sprite.spritecollide(player, enemy_projectiles, True):
            player.speedy = -8

        # Colisão: golpe da chave × player
        wrench_rect = boss.get_wrench_rect()
        if wrench_rect and player.rect.colliderect(wrench_rect):
            player.speedy  = -10
            player.rect.x += 60 * boss.direction

        # Colisão: minas × player — dispara explosão
        mine_player_hits = pygame.sprite.spritecollide(player, mines_group, False)
        for mine in mine_player_hits:
            mine.explode()
            player.speedy = -8

        # Desenha
        window.fill((30, 25, 20))  # fundo preto para cobrir área abaixo do bg
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

        if not boss.alive:
            txt = font_big.render('CHEFÃO DERROTADO!', True, (255, 220, 50))
            window.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 40))
            pygame.display.flip()
            pygame.time.wait(3000)
            state = INIT

        pygame.display.flip()

    return state