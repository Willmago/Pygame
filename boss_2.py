import pygame
from config import JARE_GV, QUIT, WIN
from classes import *

# ===== Main =====
def reset_game():
    return (Player_2(), Boss(), PhaseManager(),
            [], [], [], [], [], [], 0, 0, False, False)

def main():
    (player, boss, pm,
    fall_bullets, horiz_missiles, diag_missiles,
    bolinhas, player_bullets, particles,
    score, tick, game_over, win) = reset_game()
    state = JARE_GV

    while state == JARE_GV:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: state = QUIT
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: state = INIT
                elif event.key == pygame.K_r and game_over:
                    (player, boss, pm,
                    fall_bullets, horiz_missiles, diag_missiles,
                    bolinhas, player_bullets, particles,
                    score, tick, game_over, win) = reset_game()
                elif event.key == pygame.K_RETURN and game_over:
                    state = BOSS3

        if not game_over:
            tick += 1
            player.update(keys)
            boss.update()

            pb = player.shoot()
            if pb: player_bullets.append(pb)

            player_died = pm.update(boss, fall_bullets, horiz_missiles,
                                    diag_missiles, bolinhas, player, particles)
            if player_died: game_over=True; win=False

            for o in (fall_bullets+horiz_missiles+diag_missiles+
                    bolinhas+player_bullets+particles):
                o.update()
            fall_bullets   = [b for b in fall_bullets   if b.alive]
            horiz_missiles = [h for h in horiz_missiles if h.alive]
            diag_missiles  = [d for d in diag_missiles  if d.alive]
            bolinhas       = [b for b in bolinhas       if b.alive]
            player_bullets = [b for b in player_bullets if b.alive]
            particles      = [p for p in particles      if p.life>0]

            prect = player.rect()
            def hit(obj):
                nonlocal game_over, win
                if obj.rect().colliderect(prect) and player.take_hit():
                    obj.alive=False
                    for _ in range(12):
                        particles.append(Particle(
                            player.x+PLAYER_W//2, player.y+PLAYER_H//2, C_RED))
                    if player.hp<=0: game_over=True; win=False
            for b in fall_bullets:   hit(b)
            for h in horiz_missiles: hit(h)
            for d in diag_missiles:  hit(d)
            for b in bolinhas:       hit(b)

            brect = boss.rect()
            for b in player_bullets:
                if b.rect().colliderect(brect):
                    b.alive=False
                    if boss.take_hit():
                        score+=100
                        for _ in range(10):
                            particles.append(Particle(
                                BOSS_X+BOSS_W//2, BOSS_Y+BOSS_H//2, C_YELLOW))
                        if boss.hp<=0: game_over=True; win=True; state == WIN

        # ── Desenho ──────────────────────────────────────────────────────
        draw_background(window, tick)
        pm.draw_bg(window, tick)          # cauda — plano de fundo
        for b in player_bullets: b.draw(window)
        boss.draw(window, tick)
        for b in fall_bullets:   b.draw(window)
        for h in horiz_missiles: h.draw(window)
        for d in diag_missiles:  d.draw(window)
        for b in bolinhas:       b.draw(window)
        player.draw(window)
        for p in particles: p.draw(window)
        draw_hud(window, score, pm.phase)  # HUD na frente da cauda
        pm.draw_fg(window, tick)           # banner de transição no topo
        if game_over: draw_game_over(window, win)
        if tick < 240 and not game_over:
            lines = [
                "WASD/Setas: mover  |  W/Espaço: pular  |  Z/Ctrl: atirar",
                "Fase 1: desvie das cabeças  |  Fase 2: chuva de mísseis  |  Fase 3: rasteiros + bolinhas"
            ]
            for i,line in enumerate(lines):
                t = font_small.render(line,True,C_BLACK)
                window.blit(t,(WIDTH//2-t.get_width()//2+1,HEIGHT-65+i*22+1))
                window.blit(font_small.render(line,True,C_WHITE),
                            (WIDTH//2-t.get_width()//2,HEIGHT-65+i*22))
        pygame.display.flip()
    return state
# ===== Cuphead-style Boss Fight — 3 Fases =====
def boss_2():

    state = main()
    return state
