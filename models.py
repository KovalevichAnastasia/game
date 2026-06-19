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
        self.speed_x = 0
        self.speed_y = -BALL_SPEED_Y
        self.active = True

    def update(self, wind=0.0):
        if not self.active:
            return
        self.move(self.speed_x + wind, self.speed_y)
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.speed_x = abs(self.speed_x)
        elif self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.speed_x = -abs(self.speed_x)
        if self.y - self.radius <= 0:
            self.speed_y = -self.speed_y

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed_y = -BALL_SPEED_Y
        self.speed_x = 0

class AnimalModel(GameObject):
    def __init__(self, x, y, speed, is_golden=False):
        super().__init__(x, y, ANIMAL_RADIUS * 2, ANIMAL_RADIUS * 2)
        self.radius = ANIMAL_RADIUS
        self.falling = False
        self.speed_y = speed
        self.caught = False
        self.lost = False
        self.is_golden = is_golden

    def update(self, wind=0.0):
        if self.falling:
            self.move(wind, self.speed_y)

class CloudModel(GameObject):
    def __init__(self):
        x = random.randint(0, WIDTH - CLOUD_WIDTH)
        y = random.randint(20, 100)
        super().__init__(x, y, CLOUD_WIDTH, CLOUD_HEIGHT)
        self.speed = CLOUD_SPEED * random.choice([-1, 1])
        self.shoot_timer = random.randint(100, 300)

    def update(self, wind=0.0):
        self.move(self.speed + wind, 0)
        if self.x <= 0 or self.x + self.width >= WIDTH:
            self.speed = -self.speed
        self.shoot_timer -= 1

class LightningModel(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, LIGHTNING_WIDTH, LIGHTNING_HEIGHT)
        self.speed = LIGHTNING_SPEED
        self.active = True

    def update(self, wind=0.0):
        if self.active:
            self.move(wind, self.speed)

class BirdProjectileModel(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, BIRD_PROJECTILE_RADIUS * 2, BIRD_PROJECTILE_RADIUS * 2)
        self.speed_y = BIRD_PROJECTILE_SPEED
        self.active = True

    def update(self, wind=0.0):
        if self.active:
            self.move(wind, self.speed_y)

class BirdModel(GameObject):
    def __init__(self):
        y = random.randint(5, 60)
        super().__init__(-BIRD_WIDTH, y, BIRD_WIDTH, BIRD_HEIGHT)
        self.speed_x = BIRD_SPEED if random.random() < 0.5 else -BIRD_SPEED
        if self.speed_x < 0:
            self.x = WIDTH + BIRD_WIDTH
        self.active = True
        self.shoot_timer = random.randint(60, 150)

    def update(self, wind=0.0):
        if not self.active:
            return
        self.move(self.speed_x + wind, 0)
        self.shoot_timer -= 1
        if self.x < -BIRD_WIDTH * 2 or self.x > WIDTH + BIRD_WIDTH * 2:
            self.active = False

class HawkStoneModel(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, HAWK_STONE_RADIUS * 2, HAWK_STONE_RADIUS * 2)
        self.speed_y = HAWK_STONE_SPEED
        self.active = True

    def update(self, wind=0.0):
        if self.active:
            self.move(wind, self.speed_y)

class HawkBossModel(GameObject):
    def __init__(self):
        super().__init__(WIDTH // 2 - HAWK_WIDTH // 2, 5, HAWK_WIDTH, HAWK_HEIGHT)
        self.hp = HAWK_HP
        self.active = True
        self.speed_x = HAWK_SPEED * random.choice([-1, 1])
        self.shoot_timer = 60
        self.hit_cooldown = 0

    def update(self, wind=0.0):
        if not self.active:
            return
        self.move(self.speed_x, 0)
        if self.x <= 0 or self.x + self.width >= WIDTH:
            self.speed_x = -self.speed_x
        self.shoot_timer -= 1
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

class GameState:
    def __init__(self):
        self.player = PlayerModel()
        self.balls = [BallModel()]
        self.animals = []
        self.clouds = []
        self.lightnings = []
        self.birds = []
        self.bird_projectiles = []
        self.hawk_boss = None
        self.hawk_stones = []
        self.level = 1
        self.combo_timer = 0
        self.wind_speed = 0.0
        self.wind_timer = 0
        self.wind_cooldown = 0
        self.bird_spawn_timer = random.randint(300, 600)
        self.state = "MENU"
        self.high_score = self.load_high_score()
        self.last_score = self.load_last_score()
        self.load_level(1)

    def load_level(self, level):
        self.level = level
        self.animals = []
        self.lightnings = []
        self.birds = []
        self.bird_projectiles = []
        self.hawk_boss = None
        self.hawk_stones = []

        if self.level >= 5:
            if len(self.balls) < 2:
                self.balls = [BallModel(), BallModel()]
        else:
            self.balls = [BallModel()]

        for b in self.balls:
            b.reset()

        self.combo_timer = 0
        self.wind_speed = 0.0
        self.wind_timer = 0

        if level == 1:
            self.wind_cooldown = -1
            self.clouds = []
        elif level == 2:
            self.wind_cooldown = 1200
            self.clouds = [CloudModel() for _ in range(2)]
        elif level == 3:
            self.wind_cooldown = -1
            self.clouds = []
        elif level == 4:
            self.wind_cooldown = -1
            self.hawk_boss = HawkBossModel()
            self.clouds = []
        elif level == 7:
            self.wind_cooldown = -1
            self.hawk_boss = HawkBossModel()
            self.hawk_boss.hp = 12
            self.clouds = []
        else:
            self.wind_cooldown = -1
            self.clouds = [CloudModel() for _ in range(min(2 + level, 5))]

        if level == 3:
            speed = 4.5
            for row in range(3):
                for col in range(8):
                    is_golden = random.random() < 0.1
                    self.animals.append(AnimalModel(100 + col * 80, 150 + row * 60, speed, is_golden))
            self.bird_spawn_timer = random.randint(60, 150)
        elif level not in (4, 7):
            speed = 3.0 + (level - 1) * 1.5
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

        active_balls = [b for b in self.balls if b.active]
        if not active_balls:
            p.lives -= 1
            p.combo_count = 0
            if p.lives <= 0:
                self.state = "GAME_OVER"
                self.save_game_results()
            else:
                for b in self.balls:
                    b.active = True
                    b.reset()

        for b in self.balls:
            if not b.active:
                continue

            if b.y + b.radius >= p.y and b.y - b.radius <= p.y + p.height:
                if p.x <= b.x <= p.x + p.width:
                    b.y = p.y - b.radius
                    b.speed_y = -abs(b.speed_y)
                    hit_pos = (b.x - p.x) / p.width
                    b.speed_x = (hit_pos - 0.5) * 10

            if b.y >= HEIGHT:
                b.active = False

            for bird in self.birds:
                if bird.active:
                    dist = math.hypot(b.x - (bird.x + bird.width//2), b.y - (bird.y + bird.height//2))
                    if dist <= b.radius + max(bird.width, bird.height)//2:
                        bird.active = False
                        b.speed_y = -b.speed_y
                        p.score += 30
                        if hasattr(self, 'birds_to_defeat') and self.birds_to_defeat > 0:
                            self.birds_to_defeat -= 1

            if self.hawk_boss and self.hawk_boss.active:
                hb = self.hawk_boss
                dist = math.hypot(b.x - (hb.x + hb.width//2), b.y - (hb.y + hb.height//2))
                if dist <= b.radius + max(hb.width, hb.height)//2:
                    b.speed_y = -b.speed_y
                    if hb.hit_cooldown <= 0:
                        hb.hp -= 1
                        hb.hit_cooldown = 30
                        if hb.hp <= 0:
                            hb.active = False
                            p.score += 500

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

        for proj in self.bird_projectiles:
            if proj.active and proj.y + proj.height >= p.y and proj.y <= p.y + p.height:
                if p.x <= proj.x <= p.x + p.width:
                    p.lives -= 1
                    proj.active = False
                    if p.lives <= 0:
                        self.state = "GAME_OVER"
                        self.save_game_results()
            if proj.y > HEIGHT:
                proj.active = False
        self.bird_projectiles = [p for p in self.bird_projectiles if p.active]

        for st in self.hawk_stones:
            if st.active and st.y + st.height >= p.y and st.y <= p.y + p.height:
                if p.x <= st.x <= p.x + p.width:
                    p.lives -= 1
                    st.active = False
                    if p.lives <= 0:
                        self.state = "GAME_OVER"
                        self.save_game_results()
            if st.y > HEIGHT:
                st.active = False
        self.hawk_stones = [s for s in self.hawk_stones if s.active]

        level_complete = False

        if self.level in (4, 7):
            if self.hawk_boss and not self.hawk_boss.active:
                level_complete = True
        else:
            all_caught_or_lost = True
            for a in self.animals:
                if not a.caught and not a.lost:
                    all_caught_or_lost = False
                    if not a.falling:
                        for b in self.balls:
                            if b.active:
                                dist = math.hypot(b.x - a.x, b.y - a.y)
                                if dist <= b.radius + a.radius:
                                    a.falling = True
                                    b.speed_y = -b.speed_y
                    else:
                        if a.y + a.radius >= p.y and a.y - a.radius <= p.y + p.height:
                            if p.x <= a.x <= p.x + p.width:
                                a.caught = True
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
            if all_caught_or_lost:
                level_complete = True

        if level_complete and self.state == "PLAYING":
            self.load_level(self.level + 1)

    def update(self):
        if self.state != "PLAYING":
            return

        if self.combo_timer > 0:
            self.combo_timer -= 1

        if self.wind_timer > 0:
            self.wind_timer -= 1
            if self.wind_timer <= 0:
                self.wind_speed = 0.0
                if self.level == 2:
                    self.wind_cooldown = 1200
        else:
            if self.wind_cooldown > 0:
                self.wind_cooldown -= 1
            elif self.wind_cooldown == 0 and self.level == 2:
                self.wind_speed = random.choice([-2.0, 2.0]) * random.uniform(0.5, 1.5)
                self.wind_timer = random.randint(120, 240)

        for b in self.balls:
            b.update(self.wind_speed)

        for cloud in self.clouds:
            cloud.update(self.wind_speed)
        for l in self.lightnings:
            l.update(self.wind_speed)
        for a in self.animals:
            a.update(self.wind_speed)

        if self.level == 3:
            self.bird_spawn_timer -= 1
            if self.bird_spawn_timer <= 0:
                self.birds.append(BirdModel())
                self.bird_spawn_timer = random.randint(80, 160)
        elif self.level not in (1, 2, 4, 7):
            self.bird_spawn_timer -= 1
            if self.bird_spawn_timer <= 0:
                self.birds.append(BirdModel())
                self.bird_spawn_timer = random.randint(400, 800)

        for bird in self.birds:
            bird.update(self.wind_speed)
            if bird.active and bird.shoot_timer <= 0:
                self.bird_projectiles.append(BirdProjectileModel(bird.x + bird.width//2, bird.y + bird.height))
                bird.shoot_timer = random.randint(60, 150)
        self.birds = [b for b in self.birds if b.active]

        for bp in self.bird_projectiles:
            bp.update(self.wind_speed)

        if self.hawk_boss and self.hawk_boss.active:
            self.hawk_boss.update(self.wind_speed)
            if self.hawk_boss.shoot_timer <= 0:
                self.hawk_stones.append(HawkStoneModel(self.hawk_boss.x + self.hawk_boss.width//2, self.hawk_boss.y + self.hawk_boss.height))
                self.hawk_boss.shoot_timer = random.randint(40, 90)

        for st in self.hawk_stones:
            st.update(self.wind_speed)

        self.check_collisions()
