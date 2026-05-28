import random
import math
from constants import *

class GameObject:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class PlayerModel(GameObject):
    def __init__(self):
        super().__init__(WIDTH // 2 - PLAYER_WIDTH // 2, HEIGHT - 40, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.speed = PLAYER_SPEED
        self.lives = PLAYER_LIVES
        self.score = 0
        self.combo_count = 0

    def move_left(self):
        self.x -= self.speed
        if self.x < 0:
            self.x = 0

    def move_right(self):
        self.x += self.speed
        if self.x + self.width > WIDTH:
            self.x = WIDTH - self.width

class BallModel(GameObject):
    def __init__(self):
        super().__init__(WIDTH // 2, HEIGHT // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
        self.radius = BALL_RADIUS
        self.speed_x = BALL_SPEED_X * random.choice([-1, 1])
        self.speed_y = -BALL_SPEED_Y
        self.active = True

    def update(self):
        if not self.active:
            return

        self.move(self.speed_x, self.speed_y)

        if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
            self.speed_x = -self.speed_x
        if self.y - self.radius <= 0:
            self.speed_y = -self.speed_y

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed_y = -BALL_SPEED_Y
        self.speed_x = BALL_SPEED_X * random.choice([-1, 1])

class AnimalModel(GameObject):
    def __init__(self, x, y, speed, is_golden=False):
        super().__init__(x, y, ANIMAL_RADIUS * 2, ANIMAL_RADIUS * 2)
        self.radius = ANIMAL_RADIUS
        self.falling = False
        self.speed_y = speed
        self.caught = False
        self.lost = False
        self.is_golden = is_golden

    def update(self):
        if self.falling:
            self.move(0, self.speed_y)

class CloudModel(GameObject):
    def __init__(self):
        x = random.randint(0, WIDTH - CLOUD_WIDTH)
        y = random.randint(20, 100)
        super().__init__(x, y, CLOUD_WIDTH, CLOUD_HEIGHT)
        self.speed = CLOUD_SPEED * random.choice([-1, 1])
        self.shoot_timer = random.randint(100, 300)

    def update(self):
        self.move(self.speed, 0)
        if self.x <= 0 or self.x + self.width >= WIDTH:
            self.speed = -self.speed
        self.shoot_timer -= 1

class LightningModel(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, LIGHTNING_WIDTH, LIGHTNING_HEIGHT)
        self.speed = LIGHTNING_SPEED
        self.active = True

    def update(self):
        if self.active:
            self.move(0, self.speed)



class ParticleModel:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = 30
        self.color = color

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1

class GameState:
    def __init__(self):
        self.player = PlayerModel()
        self.balls = []
        self.animals = []
        self.clouds = []
        self.lightnings = []
        self.particles = []
        self.level = 1
        self.combo_timer = 0
        
        self.state = "MENU" # MENU, PLAYING, GAME_OVER, WIN
        self.high_score = self.load_high_score()
        self.last_score = self.load_last_score()
        
        self.load_level(1)

    def load_level(self, level):
        self.level = level
        self.animals = []
        self.lightnings = []
        self.particles = []
        
        self.balls = []
        for i in range(3):
            b = BallModel()
            b.speed_x += (i - 1) * 2
            self.balls.append(b)
            
        self.combo_timer = 0
        
        speed = 3.0 + (level - 1) * 1.5
        
        if self.level == 1:
            self.clouds = []
        elif self.level == 2:
            self.clouds = [CloudModel() for _ in range(2)]
        else:
            self.clouds = [CloudModel() for _ in range(min(2 + level, 5))]
            
        for row in range(3):
            for col in range(8):
                is_golden = random.random() < 0.1
                self.animals.append(AnimalModel(100 + col * 80, 150 + row * 60, speed, is_golden))

    def load_high_score(self):
        try:
            with open("save.txt", "r") as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0

    def load_last_score(self):
        try:
            with open("last_score.txt", "r") as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        if self.player.score > self.high_score:
            self.high_score = self.player.score
            with open("save.txt", "w") as f:
                f.write(str(self.high_score))

    def save_game_results(self):
        self.last_score = self.player.score
        try:
            with open("last_score.txt", "w") as f:
                f.write(str(self.last_score))
        except Exception as e:
            print(f"Error saving last score: {e}")
        self.save_high_score()

    def check_collisions(self):
        p = self.player
        for b in self.balls:
            if b.y + b.radius >= p.y and b.y - b.radius <= p.y + p.height:
                if p.x <= b.x <= p.x + p.width:
                    b.speed_y = -abs(b.speed_y)
                    hit_pos = (b.x - p.x) / p.width
                    b.speed_x = (hit_pos - 0.5) * 10
                    p.score += 1

            if b.y >= HEIGHT:
                b.active = False
        
        self.balls = [b for b in self.balls if b.active]
        if not self.balls:
            p.lives -= 1
            p.combo_count = 0
            if p.lives <= 0:
                self.state = "GAME_OVER"
                self.save_game_results()
            else:
                self.balls = []
                for i in range(3):
                    b = BallModel()
                    b.speed_x += (i - 1) * 2
                    self.balls.append(b)

        for cloud in self.clouds:
            if cloud.shoot_timer <= 0:
                self.lightnings.append(LightningModel(cloud.x + cloud.width // 2, cloud.y + cloud.height))
                cloud.shoot_timer = random.randint(100, 300)

        for l in self.lightnings:
            if l.active and l.y + l.height >= p.y and l.y <= p.y + p.height:
                if p.x <= l.x <= p.x + p.width:
                    p.lives -= 1
                    l.active = False
                    if p.lives <= 0:
                        self.state = "GAME_OVER"
                        self.save_game_results()
            if l.y > HEIGHT:
                l.active = False
        
        self.lightnings = [l for l in self.lightnings if l.active]

        all_caught_or_lost = True
        for a in self.animals:
            if not a.caught and not a.lost:
                all_caught_or_lost = False
                
                if not a.falling:
                    for b in self.balls:
                        dist = math.hypot(b.x - a.x, b.y - a.y)
                        if dist <= b.radius + a.radius:
                            a.falling = True
                            b.speed_y = -b.speed_y
                            p.score += 5
                            for _ in range(10):
                                self.particles.append(ParticleModel(a.x, a.y, (255, 105, 180)))
                            break
                else:
                    if a.y + a.radius >= p.y and a.y - a.radius <= p.y + p.height:
                        if p.x <= a.x <= p.x + p.width:
                            a.caught = True
                            for _ in range(15):
                                self.particles.append(ParticleModel(a.x, a.y, (255, 215, 0) if a.is_golden else (50, 205, 50)))
                            
                            if a.is_golden:
                                p.lives += 1
                            else:
                                p.score += 20
                                
                            p.combo_count += 1
                            if p.combo_count >= 3:
                                p.score += 50
                                p.combo_count = 0
                                self.combo_timer = 60
                    elif a.y - a.radius > HEIGHT:
                        a.lost = True
                        p.score = max(0, p.score - 15)

        if all_caught_or_lost and self.state == "PLAYING":
            self.load_level(self.level + 1)

    def update(self):
        if self.state == "PLAYING":
            if self.combo_timer > 0:
                self.combo_timer -= 1
            for b in self.balls:
                b.update()
            for cloud in self.clouds:
                cloud.update()
            for l in self.lightnings:
                l.update()
            for a in self.animals:
                a.update()
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.life > 0]
            self.check_collisions()
