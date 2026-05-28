import pygame
import os
import math
from constants import *

class GameView:
    def __init__(self, screen):
        self.screen = screen
        self.font_name = "comicsansms"
        self.font = pygame.font.SysFont(self.font_name, 36, bold=True)
        self.large_font = pygame.font.SysFont(self.font_name, 64, bold=True)
        self.title_font = pygame.font.SysFont(self.font_name, 52, bold=True)
        
        self.text_color = (255, 255, 255)
        self.shadow_color = (199, 21, 133)
        
        self.assets = {}
        self.load_assets()

    def load_image(self, name, size):
        path = os.path.join("assets", name)
        try:
            image = pygame.image.load(path).convert_alpha()
            image.set_colorkey((255, 0, 255))
            return pygame.transform.scale(image, size)
        except Exception as e:
            print(f"Не удалось загрузить {name}: {e}")
            return None

    def load_assets(self):
        self.assets['bg'] = self.load_image("bg.png", (WIDTH, HEIGHT))
        self.assets['animal'] = self.load_image("animal.png", (ANIMAL_RADIUS*2, ANIMAL_RADIUS*2))
        self.assets['golden_animal'] = self.load_image("golden_animal.png", (ANIMAL_RADIUS*2, ANIMAL_RADIUS*2))
        self.assets['cloud'] = self.load_image("cloud.png", (CLOUD_WIDTH*2, CLOUD_HEIGHT*2))
        self.assets['player'] = self.load_image("player.png", (PLAYER_WIDTH, PLAYER_HEIGHT * 5))
        self.assets['ball'] = self.load_image("ball.png", (BALL_RADIUS*3, BALL_RADIUS*3))
        self.assets['lightning'] = self.load_image("lightning.png", (LIGHTNING_WIDTH*8, LIGHTNING_HEIGHT*3))
        
    def _draw_text_with_shadow(self, text, font, x, y):
        shadow = font.render(text, True, self.shadow_color)
        self.screen.blit(shadow, (x + 3, y + 3))
        main_text = font.render(text, True, self.text_color)
        self.screen.blit(main_text, (x, y))

    def draw(self, game_state):
        if self.assets['bg']:
            self.screen.blit(self.assets['bg'], (0, 0))
        else:
            self.screen.fill((255, 182, 193))

        if game_state.state == "MENU":
            self._draw_menu(game_state)
        elif game_state.state in ["PLAYING", "GAME_OVER", "WIN"]:
            self._draw_game(game_state)
            
            if game_state.state == "GAME_OVER":
                self._draw_message("ИГРА ОКОНЧЕНА")
            elif game_state.state == "WIN":
                self._draw_message("ПОБЕДА!")

        pygame.display.flip()

    def _draw_menu(self, game_state):
        title_w, title_h = self.title_font.size("ПУШИСТЫЙ ПЕРЕПОЛОХ")
        self._draw_text_with_shadow("ПУШИСТЫЙ ПЕРЕПОЛОХ", self.title_font, WIDTH // 2 - title_w // 2, HEIGHT // 3)

        start_w, start_h = self.font.size("Нажмите ПРОБЕЛ, чтобы начать")
        self._draw_text_with_shadow("Нажмите ПРОБЕЛ, чтобы начать", self.font, WIDTH // 2 - start_w // 2, HEIGHT // 2)
        
        score_text = f"Предыдущий счет: {game_state.last_score}"
        score_w, score_h = self.font.size(score_text)
        self._draw_text_with_shadow(score_text, self.font, WIDTH // 2 - score_w // 2, HEIGHT // 2 + 50)

    def _draw_game(self, state):
        for cloud in state.clouds:
            if self.assets['cloud']:
                self.screen.blit(self.assets['cloud'], (cloud.x - cloud.width//2, cloud.y - cloud.height//2))
            else:
                pygame.draw.ellipse(self.screen, GRAY, (cloud.x, cloud.y, cloud.width, cloud.height))

        for animal in state.animals:
            if not animal.caught and not animal.lost:
                if animal.is_golden:
                    if self.assets.get('golden_animal'):
                        self.screen.blit(self.assets['golden_animal'], (animal.x - animal.radius, animal.y - animal.radius))
                    else:
                        color = (255, 215, 0)
                        pygame.draw.circle(self.screen, color, (int(animal.x), int(animal.y)), animal.radius)
                else:
                    if self.assets['animal']:
                        self.screen.blit(self.assets['animal'], (animal.x - animal.radius, animal.y - animal.radius))
                    else:
                        color = GREEN if not animal.falling else RED
                        pygame.draw.circle(self.screen, color, (int(animal.x), int(animal.y)), animal.radius)

        for l in state.lightnings:
            if 'lightning' in self.assets and self.assets['lightning']:
                img = self.assets['lightning']
                self.screen.blit(img, (l.x - img.get_width()//2, l.y))
            else:
                w = 16
                h = l.height * 1.5
                px = l.x - w // 2
                py = l.y
                
                points = [
                    (px + w * 0.7, py),
                    (px, py + h * 0.5),
                    (px + w * 0.4, py + h * 0.5),
                    (px + w * 0.1, py + h),
                    (px + w, py + h * 0.4),
                    (px + w * 0.5, py + h * 0.4)
                ]
                pygame.draw.polygon(self.screen, (255, 140, 0), points)
                
                inner_points = [
                    (px + w * 0.65, py + 2),
                    (px + 2, py + h * 0.5 - 1),
                    (px + w * 0.4, py + h * 0.48),
                    (px + w * 0.15, py + h - 2),
                    (px + w - 2, py + h * 0.42),
                    (px + w * 0.45, py + h * 0.42)
                ]
                pygame.draw.polygon(self.screen, (255, 255, 0), inner_points)

        p = state.player
        if self.assets['player']:
            self.screen.blit(self.assets['player'], (p.x, p.y - p.height * 4))
        else:
            pygame.draw.rect(self.screen, BROWN, (p.x, p.y, p.width, p.height), border_radius=10)
        
        if state.state != "GAME_OVER" and state.state != "WIN":
            for b in state.balls:
                if self.assets['ball']:
                    self.screen.blit(self.assets['ball'], (b.x - b.radius*1.5, b.y - b.radius*1.5))
                else:
                    pygame.draw.circle(self.screen, YELLOW, (int(b.x), int(b.y)), b.radius)
                    
        for particle in state.particles:
            size = max(1, particle.life // 5)
            pygame.draw.circle(self.screen, particle.color, (int(particle.x), int(particle.y)), size)

        self._draw_text_with_shadow(f"Очки: {p.score}", self.font, 10, 10)
        self._draw_text_with_shadow(f"Уровень: {state.level}", self.font, 10, 50)
        
        lives_text = f"Жизни: {p.lives}"
        lives_w, lives_h = self.font.size(lives_text)
        self._draw_text_with_shadow(lives_text, self.font, WIDTH - lives_w - 10, 10)

        if state.combo_timer > 0:
            combo_text = "КОМБО! +50"
            combo_w, combo_h = self.large_font.size(combo_text)
            self._draw_text_with_shadow(combo_text, self.large_font, WIDTH // 2 - combo_w // 2, HEIGHT // 3)

    def _draw_message(self, text):
        msg_w, msg_h = self.large_font.size(text)
        self._draw_text_with_shadow(text, self.large_font, WIDTH // 2 - msg_w // 2, HEIGHT // 2 - 30)
        
        sub_msg = "Нажмите ESC для выхода в меню"
        sub_w, sub_h = self.font.size(sub_msg)
        self._draw_text_with_shadow(sub_msg, self.font, WIDTH // 2 - sub_w // 2, HEIGHT // 2 + 50)
