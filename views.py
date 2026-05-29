import pygame
import os
import random
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
        
        self.wind_particles = []
        for _ in range(30):
            self.wind_particles.append([random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(30, 150)])


    def load_image(self, name, size):
        path = os.path.join("assets", name)
        try:
            image = pygame.image.load(path).convert_alpha()
            image.set_colorkey((255, 0, 255))
            return pygame.transform.scale(image, size)
        except Exception as e:
            # print(f"Не удалось загрузить {name}: {e}")
            return None

    def load_assets(self):
        self.assets['bg'] = self.load_image("bg.png", (WIDTH, HEIGHT))
        self.assets['animal'] = self.load_image("animal.png", (ANIMAL_RADIUS*2, ANIMAL_RADIUS*2))
        self.assets['golden_animal'] = self.load_image("golden_animal.png", (ANIMAL_RADIUS*2, ANIMAL_RADIUS*2))
        self.assets['cloud'] = self.load_image("cloud.png", (CLOUD_WIDTH*2, CLOUD_HEIGHT*2))
        self.assets['player'] = self.load_image("player.png", (PLAYER_WIDTH, PLAYER_HEIGHT * 5))
        self.assets['ball'] = self.load_image("ball.png", (BALL_RADIUS*3, BALL_RADIUS*3))
        self.assets['bird'] = self.load_image("bird.png", (BIRD_WIDTH, BIRD_HEIGHT))
        self.assets['stone'] = self.load_image("stone.png", (HAWK_STONE_RADIUS*4, HAWK_STONE_RADIUS*4))
        self.assets['hawk_boss'] = self.load_image("hawk_boss.png", (HAWK_WIDTH, HAWK_HEIGHT))
        self.assets['capybara'] = self.load_image("capybara.png", (ANIMAL_RADIUS*2, ANIMAL_RADIUS*2))
        
    def _draw_text_with_shadow(self, text, font, x, y):
        """Отрисовывает текст с красивой тенью для объема"""
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
        if state.wind_speed != 0:
            for p in self.wind_particles:
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

        for cloud in state.clouds:
            if self.assets['cloud']:
                self.screen.blit(self.assets['cloud'], (cloud.x - cloud.width//2, cloud.y - cloud.height//2))
            else:
                pygame.draw.ellipse(self.screen, GRAY, (cloud.x, cloud.y, cloud.width, cloud.height))

        for animal in state.animals:
            if not animal.caught and not animal.lost:
                if getattr(animal, 'is_capybara', False):
                    if self.assets.get('capybara'):
                        self.screen.blit(self.assets['capybara'], (animal.x - animal.radius, animal.y - animal.radius))
                    else:
                        pygame.draw.circle(self.screen, (180, 130, 80), (int(animal.x), int(animal.y)), animal.radius)
                elif animal.is_golden:
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
            
            pygame.draw.polygon(self.screen, (255, 255, 0), points)
            pygame.draw.polygon(self.screen, (255, 255, 255), points, 1)

        # Птицы
        for bird in getattr(state, 'birds', []):
            if self.assets.get('bird'):
                self.screen.blit(self.assets['bird'], (bird.x, bird.y))
            else:
                pygame.draw.ellipse(self.screen, (100, 100, 255), (bird.x, bird.y, bird.width, bird.height))
                pygame.draw.polygon(self.screen, (150, 150, 255), [(bird.x + bird.width//2, bird.y), (bird.x + bird.width//2 - 10, bird.y - 15), (bird.x + bird.width//2 + 10, bird.y - 15)])
            
        # Снаряды птиц
        for proj in getattr(state, 'bird_projectiles', []):
            if self.assets.get('stone'):
                stone_img = pygame.transform.scale(self.assets['stone'], (int(proj.width), int(proj.height)))
                self.screen.blit(stone_img, (proj.x - proj.width//2, proj.y - proj.height//2))
            else:
                pygame.draw.circle(self.screen, (150, 50, 50), (int(proj.x), int(proj.y)), int(proj.width//2))

        # Ястреб (Босс)
        if getattr(state, 'hawk_boss', None) and state.hawk_boss.active:
            hb = state.hawk_boss
            if self.assets.get('hawk_boss'):
                self.screen.blit(self.assets['hawk_boss'], (hb.x, hb.y))
            else:
                pygame.draw.rect(self.screen, (139, 0, 0), (hb.x, hb.y, hb.width, hb.height))
                pygame.draw.circle(self.screen, (255, 0, 0), (int(hb.x + hb.width * 0.25), int(hb.y + hb.height * 0.25)), 10)
                pygame.draw.circle(self.screen, (255, 0, 0), (int(hb.x + hb.width * 0.75), int(hb.y + hb.height * 0.25)), 10)
            
            # Полоска здоровья
            hp_w = hb.width
            pygame.draw.rect(self.screen, (255, 0, 0), (hb.x, hb.y - 20, hp_w, 10))
            pygame.draw.rect(self.screen, (0, 255, 0), (hb.x, hb.y - 20, int(hp_w * (hb.hp / HAWK_HP)), 10))

        # Камни босса
        for st in getattr(state, 'hawk_stones', []):
            if self.assets.get('stone'):
                self.screen.blit(self.assets['stone'], (st.x, st.y))
            else:
                pygame.draw.rect(self.screen, (105, 105, 105), (st.x, st.y, st.width, st.height))

        p = state.player
        if self.assets['player']:
            self.screen.blit(self.assets['player'], (p.x, p.y - p.height * 4))
        else:
            pygame.draw.rect(self.screen, BROWN, (p.x, p.y, p.width, p.height), border_radius=10)
        
        if state.state != "GAME_OVER" and state.state != "WIN":
            if hasattr(state, 'balls'):
                for b in state.balls:
                    if not b.active: continue
                    # Оранжевый контур (светлячок)
                    pygame.draw.circle(self.screen, (255, 165, 0), (int(b.x), int(b.y)), b.radius + 3)
                    
                    if self.assets['ball']:
                        self.screen.blit(self.assets['ball'], (b.x - b.radius*1.5, b.y - b.radius*1.5))
                    else:
                        pygame.draw.circle(self.screen, YELLOW, (int(b.x), int(b.y)), b.radius)

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
