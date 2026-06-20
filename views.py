"""
views.py — Отрисовка всех игровых объектов и экранов.

Отвечает только за визуализацию (принцип SRP):
не содержит игровой логики и не изменяет состояние игры.
"""

import pygame
import os
import random
from constants import (
    WIDTH, HEIGHT,
    PLAYER_WIDTH, PLAYER_HEIGHT,
    ANIMAL_RADIUS,
    CLOUD_WIDTH, CLOUD_HEIGHT,
    BALL_RADIUS,
    HAWK_WIDTH, HAWK_HEIGHT, HAWK_HP,
    HAWK_STONE_RADIUS, BIRD_PROJECTILE_RADIUS,
    BIRD_WIDTH, BIRD_HEIGHT,
    BROWN, GRAY, GREEN, RED, YELLOW,
)


class GameView:
    """
    Отвечает за отрисовку всего, что видит игрок.

    Получает объект GameState и рисует его содержимое на экране.
    Не хранит игровых данных и не влияет на логику.
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._font_name = "comicsansms"
        self._font = pygame.font.SysFont(self._font_name, 36, bold=True)
        self._large_font = pygame.font.SysFont(self._font_name, 64, bold=True)
        self._title_font = pygame.font.SysFont(self._font_name, 52, bold=True)
        self._text_color = (255, 255, 255)
        self._shadow_color = (199, 21, 133)
        self._assets: dict = {}
        self._load_assets()
        self._wind_particles = [
            [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(30, 150)]
            for _ in range(30)
        ]

    def _load_image(self, name: str, size: tuple) -> pygame.Surface | None:
        """Загрузить изображение из папки assets. Возвращает None при ошибке."""
        path = os.path.join("assets", name)
        try:
            image = pygame.image.load(path).convert_alpha()
            image.set_colorkey((255, 0, 255))
            return pygame.transform.scale(image, size)
        except Exception:
            return None

    def _load_assets(self) -> None:
        """Загрузить все игровые спрайты."""
        self._assets['bg'] = self._load_image("bg.png", (WIDTH, HEIGHT))
        self._assets['animal'] = self._load_image("animal.png", (ANIMAL_RADIUS * 2, ANIMAL_RADIUS * 2))
        self._assets['golden_animal'] = self._load_image("golden_animal.png", (ANIMAL_RADIUS * 2, ANIMAL_RADIUS * 2))
        self._assets['cloud'] = self._load_image("cloud.png", (CLOUD_WIDTH * 2, CLOUD_HEIGHT * 2))
        self._assets['player'] = self._load_image("player.png", (PLAYER_WIDTH, PLAYER_HEIGHT * 5))
        self._assets['ball'] = self._load_image("ball.png", (BALL_RADIUS * 3, BALL_RADIUS * 3))
        self._assets['bird'] = self._load_image("bird.png", (BIRD_WIDTH, BIRD_HEIGHT))
        self._assets['stone'] = self._load_image("stone.png", (HAWK_STONE_RADIUS * 4, HAWK_STONE_RADIUS * 4))
        self._assets['hawk_boss'] = self._load_image("hawk_boss.png", (HAWK_WIDTH, HAWK_HEIGHT))
        self._assets['capybara'] = self._load_image("capybara.png", (ANIMAL_RADIUS * 2, ANIMAL_RADIUS * 2))

    def _draw_text_with_shadow(self, text: str, font: pygame.font.Font,
                                x: int, y: int) -> None:
        """Нарисовать текст с тенью для лучшей читаемости."""
        self.screen.blit(font.render(text, True, self._shadow_color), (x + 3, y + 3))
        self.screen.blit(font.render(text, True, self._text_color), (x, y))

    def draw(self, game_state) -> None:
        """Главный метод отрисовки: выбирает нужный экран по состоянию игры."""
        if self._assets['bg']:
            self.screen.blit(self._assets['bg'], (0, 0))
        else:
            self.screen.fill((255, 182, 193))

        if game_state.state == "MENU":
            self._draw_menu(game_state)
        elif game_state.state in ("PLAYING", "GAME_OVER", "WIN"):
            self._draw_game(game_state)
            if game_state.state == "GAME_OVER":
                self._draw_message("ИГРА ОКОНЧЕНА")
            elif game_state.state == "WIN":
                self._draw_message("ПОБЕДА!")

        if getattr(game_state, 'paused', False) and game_state.state == "PLAYING":
            self._draw_pause()

        pygame.display.flip()

    def _draw_menu(self, game_state) -> None:
        """Отрисовать главное меню с заголовком и подсказками."""
        title = "ПУШИСТЫЙ ПЕРЕПОЛОХ"
        title_w, _ = self._title_font.size(title)
        self._draw_text_with_shadow(title, self._title_font, WIDTH // 2 - title_w // 2, HEIGHT // 3)

        start = "Нажмите ПРОБЕЛ, чтобы начать"
        start_w, _ = self._font.size(start)
        self._draw_text_with_shadow(start, self._font, WIDTH // 2 - start_w // 2, HEIGHT // 2)

        score_text = f"Предыдущий счет: {game_state.last_score}"
        score_w, _ = self._font.size(score_text)
        self._draw_text_with_shadow(score_text, self._font, WIDTH // 2 - score_w // 2, HEIGHT // 2 + 50)

    def _draw_game(self, state) -> None:
        """Отрисовать все игровые объекты: ветер, облака, зверьков, молнии, птиц, босса, мяч, HUD."""
        self._draw_wind_particles(state)
        self._draw_clouds(state)
        self._draw_animals(state)
        self._draw_lightnings(state)
        self._draw_birds(state)
        self._draw_hawk_boss(state)
        self._draw_player(state)
        self._draw_balls(state)
        self._draw_hud(state)

    def _draw_wind_particles(self, state) -> None:
        """Нарисовать частицы ветра, если ветер активен."""
        if state.wind_speed == 0:
            return
        for p in self._wind_particles:
            p[0] += state.wind_speed * 8
            if state.wind_speed > 0 and p[0] > WIDTH:
                p[0] = -p[2]
                p[1] = random.randint(0, HEIGHT)
            elif state.wind_speed < 0 and p[0] < -p[2]:
                p[0] = WIDTH
                p[1] = random.randint(0, HEIGHT)
            surf = pygame.Surface((p[2], 3), pygame.SRCALPHA)
            surf.fill((255, 255, 255, 150))
            self.screen.blit(surf, (p[0], p[1]))

    def _draw_clouds(self, state) -> None:
        """Нарисовать все облака."""
        for cloud in state.clouds:
            img = self._assets.get('cloud')
            if img:
                self.screen.blit(img, (cloud.x - cloud.width // 2, cloud.y - cloud.height // 2))
            else:
                pygame.draw.ellipse(self.screen, GRAY, (cloud.x, cloud.y, cloud.width, cloud.height))

    def _draw_animals(self, state) -> None:
        """Нарисовать всех активных зверьков."""
        for animal in state.animals:
            if animal.caught or animal.lost:
                continue
            if getattr(animal, 'is_capybara', False):
                img = self._assets.get('capybara')
            elif animal.is_golden:
                img = self._assets.get('golden_animal')
            else:
                img = self._assets.get('animal')

            if img:
                self.screen.blit(img, (animal.x - animal.radius, animal.y - animal.radius))
            else:
                color = (255, 215, 0) if animal.is_golden else (GREEN if not animal.falling else RED)
                pygame.draw.circle(self.screen, color, (int(animal.x), int(animal.y)), animal.radius)

    def _draw_lightnings(self, state) -> None:
        """Нарисовать все молнии."""
        for lightning in state.lightnings:
            w, h = 16, lightning.height * 1.5
            px, py = lightning.x - w // 2, lightning.y
            points = [
                (px + w * 0.7, py), (px, py + h * 0.5),
                (px + w * 0.4, py + h * 0.5), (px + w * 0.1, py + h),
                (px + w, py + h * 0.4), (px + w * 0.5, py + h * 0.4),
            ]
            pygame.draw.polygon(self.screen, (255, 255, 0), points)
            pygame.draw.polygon(self.screen, (255, 255, 255), points, 1)

    def _draw_birds(self, state) -> None:
        """Нарисовать птиц и их снаряды."""
        for bird in state.birds:
            img = self._assets.get('bird')
            if img:
                self.screen.blit(img, (bird.x, bird.y))
            else:
                pygame.draw.ellipse(self.screen, (100, 100, 255),
                                    (bird.x, bird.y, bird.width, bird.height))

        for proj in state.bird_projectiles:
            img = self._assets.get('stone')
            if img:
                scaled = pygame.transform.scale(img, (int(proj.width), int(proj.height)))
                self.screen.blit(scaled, (proj.x - proj.width // 2, proj.y - proj.height // 2))
            else:
                pygame.draw.circle(self.screen, (150, 50, 50),
                                   (int(proj.x), int(proj.y)), int(proj.width // 2))

    def _draw_hawk_boss(self, state) -> None:
        """Нарисовать босса-ястреба и его шкалу здоровья."""
        if not (state.hawk_boss and state.hawk_boss.active):
            return
        hb = state.hawk_boss
        img = self._assets.get('hawk_boss')
        if img:
            self.screen.blit(img, (hb.x, hb.y))
        else:
            pygame.draw.rect(self.screen, (139, 0, 0), (hb.x, hb.y, hb.width, hb.height))

        # HP-бар
        max_hp = HAWK_HP if state.level == 4 else HAWK_HP * 2
        bar_total_w, bar_h, divider = 240, 22, 4
        seg_w = (bar_total_w - divider * (max_hp - 1)) // max_hp
        bar_x = int(hb.x + hb.width // 2 - bar_total_w // 2)
        bar_y = hb.y + hb.height + 8
        pygame.draw.rect(self.screen, (0, 0, 0),
                         pygame.Rect(bar_x - 3, bar_y - 3, bar_total_w + 6, bar_h + 6),
                         border_radius=6)
        for i in range(max_hp):
            sx = bar_x + i * (seg_w + divider)
            seg_rect = pygame.Rect(sx, bar_y, seg_w, bar_h)
            if i < hb.hp:
                pygame.draw.rect(self.screen, (210, 30, 30), seg_rect, border_radius=4)
                pygame.draw.rect(self.screen, (255, 120, 120),
                                 pygame.Rect(sx + 3, bar_y + 3, seg_w - 6, bar_h // 3),
                                 border_radius=2)
            else:
                pygame.draw.rect(self.screen, (70, 70, 70), seg_rect, border_radius=4)
            pygame.draw.rect(self.screen, (0, 0, 0), seg_rect, 2, border_radius=4)

        for stone in state.hawk_stones:
            img = self._assets.get('stone')
            if img:
                self.screen.blit(img, (stone.x, stone.y))
            else:
                pygame.draw.rect(self.screen, (105, 105, 105),
                                 (stone.x, stone.y, stone.width, stone.height))

    def _draw_player(self, state) -> None:
        """Нарисовать платформу игрока."""
        p = state.player
        img = self._assets.get('player')
        if img:
            self.screen.blit(img, (p.x, p.y - p.height * 4))
        else:
            pygame.draw.rect(self.screen, BROWN, (p.x, p.y, p.width, p.height), border_radius=10)

    def _draw_balls(self, state) -> None:
        """Нарисовать все активные мячи."""
        if state.state in ("GAME_OVER", "WIN"):
            return
        for b in state.balls:
            if not b.active:
                continue
            pygame.draw.circle(self.screen, (255, 165, 0), (int(b.x), int(b.y)), b.radius + 3)
            img = self._assets.get('ball')
            if img:
                self.screen.blit(img, (b.x - b.radius * 1.5, b.y - b.radius * 1.5))
            else:
                pygame.draw.circle(self.screen, YELLOW, (int(b.x), int(b.y)), b.radius)

    def _draw_hud(self, state) -> None:
        """Нарисовать HUD: очки, уровень, жизни, комбо."""
        p = state.player
        self._draw_text_with_shadow(f"Очки: {p.score}", self._font, 10, 10)
        self._draw_text_with_shadow(f"Уровень: {state.level}", self._font, 10, 50)
        lives_text = f"Жизни: {p.lives}"
        lives_w, _ = self._font.size(lives_text)
        self._draw_text_with_shadow(lives_text, self._font, WIDTH - lives_w - 10, 10)
        if state.combo_timer > 0:
            combo = "КОМБО! +50"
            combo_w, _ = self._large_font.size(combo)
            self._draw_text_with_shadow(combo, self._large_font, WIDTH // 2 - combo_w // 2, HEIGHT // 3)

    def _draw_message(self, text: str) -> None:
        """Нарисовать крупное сообщение по центру экрана (Game Over / Win)."""
        msg_w, _ = self._large_font.size(text)
        self._draw_text_with_shadow(text, self._large_font, WIDTH // 2 - msg_w // 2, HEIGHT // 2 - 30)
        sub = "Нажмите ESC для выхода в меню"
        sub_w, _ = self._font.size(sub)
        self._draw_text_with_shadow(sub, self._font, WIDTH // 2 - sub_w // 2, HEIGHT // 2 + 50)

    def _draw_pause(self) -> None:
        """Нарисовать полупрозрачный экран паузы."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        pause_text = "ПАУЗА"
        pw, _ = self._large_font.size(pause_text)
        self._draw_text_with_shadow(pause_text, self._large_font, WIDTH // 2 - pw // 2, HEIGHT // 2 - 40)
        hint = "Нажмите P для продолжения"
        hw, _ = self._font.size(hint)
        self._draw_text_with_shadow(hint, self._font, WIDTH // 2 - hw // 2, HEIGHT // 2 + 30)
