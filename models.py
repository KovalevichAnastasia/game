"""
models.py — Игровые модели и бизнес-логика.

Содержит классы сущностей, менеджеры подсистем (очки, уровни, коллизии)
и главный класс GameState, который их координирует.
"""

import random
import math
from constants import (
    WIDTH, HEIGHT,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_LIVES,
    BALL_RADIUS, BALL_SPEED_Y,
    ANIMAL_RADIUS, ANIMAL_GRID_ROWS, ANIMAL_GRID_COLS,
    ANIMAL_START_X, ANIMAL_START_Y, ANIMAL_COL_SPACING, ANIMAL_ROW_SPACING,
    BASE_ANIMAL_SPEED, ANIMAL_SPEED_INCREMENT, GOLDEN_ANIMAL_CHANCE,
    CLOUD_WIDTH, CLOUD_HEIGHT, CLOUD_SPEED,
    LIGHTNING_WIDTH, LIGHTNING_HEIGHT, LIGHTNING_SPEED,
    BIRD_WIDTH, BIRD_HEIGHT, BIRD_SPEED,
    BIRD_PROJECTILE_RADIUS, BIRD_PROJECTILE_SPEED,
    HAWK_WIDTH, HAWK_HEIGHT, HAWK_SPEED, HAWK_HP,
    HAWK_STONE_RADIUS, HAWK_STONE_SPEED,
)


# =============================================================================
# Базовые классы сущностей
# =============================================================================

class GameObject:
    """Базовый класс для всех игровых объектов с позицией и размером."""

    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def move(self, dx: float, dy: float) -> None:
        """Переместить объект на (dx, dy)."""
        self.x += dx
        self.y += dy


class PlayerModel(GameObject):
    """Управляемая игроком платформа."""

    def __init__(self):
        super().__init__(WIDTH // 2 - PLAYER_WIDTH // 2, HEIGHT - 40,
                         PLAYER_WIDTH, PLAYER_HEIGHT)
        self.speed = PLAYER_SPEED
        self.lives = PLAYER_LIVES
        self.score = 0
        self.combo_count = 0

    def move_left(self) -> None:
        """Переместить влево, не выходя за границу экрана."""
        self.x = max(0, self.x - self.speed)

    def move_right(self) -> None:
        """Переместить вправо, не выходя за границу экрана."""
        self.x = min(WIDTH - self.width, self.x + self.speed)


class BallModel(GameObject):
    """Прыгающий мяч, которым игрок взаимодействует с объектами."""

    def __init__(self):
        super().__init__(WIDTH // 2, HEIGHT // 2, BALL_RADIUS * 2, BALL_RADIUS * 2)
        self.radius = BALL_RADIUS
        self.speed_x = 0
        self.speed_y = -BALL_SPEED_Y
        self.active = True

    def update(self, wind: float = 0.0) -> None:
        """Обновить позицию мяча с учётом стен и ветра."""
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

    def reset(self) -> None:
        """Сбросить мяч в центр экрана."""
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed_y = -BALL_SPEED_Y
        self.speed_x = 0


class AnimalModel(GameObject):
    """Зверёк, которого игрок должен поймать платформой."""

    def __init__(self, x: float, y: float, speed: float, is_golden: bool = False):
        super().__init__(x, y, ANIMAL_RADIUS * 2, ANIMAL_RADIUS * 2)
        self.radius = ANIMAL_RADIUS
        self.falling = False
        self.speed_y = speed
        self.caught = False
        self.lost = False
        self.is_golden = is_golden

    def update(self, wind: float = 0.0) -> None:
        """Падать вниз с учётом ветра."""
        if self.falling:
            self.move(wind, self.speed_y)


class CloudModel(GameObject):
    """Облако, движущееся горизонтально и периодически стреляющее молниями."""

    def __init__(self):
        x = random.randint(0, WIDTH - CLOUD_WIDTH)
        y = random.randint(20, 100)
        super().__init__(x, y, CLOUD_WIDTH, CLOUD_HEIGHT)
        self.speed = CLOUD_SPEED * random.choice([-1, 1])
        self.shoot_timer = random.randint(100, 300)

    def update(self, wind: float = 0.0) -> None:
        """Двигаться и отсчитывать таймер выстрела."""
        self.move(self.speed + wind, 0)
        if self.x <= 0 or self.x + self.width >= WIDTH:
            self.speed = -self.speed
        self.shoot_timer -= 1


class LightningModel(GameObject):
    """Молния, выпущенная облаком вниз."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, LIGHTNING_WIDTH, LIGHTNING_HEIGHT)
        self.speed = LIGHTNING_SPEED
        self.active = True

    def update(self, wind: float = 0.0) -> None:
        """Двигаться вниз."""
        if self.active:
            self.move(wind, self.speed)


class BirdProjectileModel(GameObject):
    """Камень, сброшенный птицей-врагом."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, BIRD_PROJECTILE_RADIUS * 2, BIRD_PROJECTILE_RADIUS * 2)
        self.speed_y = BIRD_PROJECTILE_SPEED
        self.active = True

    def update(self, wind: float = 0.0) -> None:
        """Двигаться вниз."""
        if self.active:
            self.move(wind, self.speed_y)


class BirdModel(GameObject):
    """Птица-враг, летящая горизонтально и стреляющая в игрока."""

    def __init__(self):
        y = random.randint(5, 60)
        super().__init__(-BIRD_WIDTH, y, BIRD_WIDTH, BIRD_HEIGHT)
        self.speed_x = BIRD_SPEED if random.random() < 0.5 else -BIRD_SPEED
        if self.speed_x < 0:
            self.x = WIDTH + BIRD_WIDTH
        self.active = True
        self.shoot_timer = random.randint(60, 150)

    def update(self, wind: float = 0.0) -> None:
        """Двигаться горизонтально; деактивироваться за пределами экрана."""
        if not self.active:
            return
        self.move(self.speed_x + wind, 0)
        self.shoot_timer -= 1
        if self.x < -BIRD_WIDTH * 2 or self.x > WIDTH + BIRD_WIDTH * 2:
            self.active = False


class HawkStoneModel(GameObject):
    """Большой камень, сброшенный боссом-ястребом."""

    def __init__(self, x: float, y: float):
        super().__init__(x, y, HAWK_STONE_RADIUS * 2, HAWK_STONE_RADIUS * 2)
        self.speed_y = HAWK_STONE_SPEED
        self.active = True

    def update(self, wind: float = 0.0) -> None:
        """Двигаться вниз."""
        if self.active:
            self.move(wind, self.speed_y)


class HawkBossModel(GameObject):
    """Босс-ястреб с очками здоровья и атакой камнями."""

    def __init__(self):
        super().__init__(WIDTH // 2 - HAWK_WIDTH // 2, 5, HAWK_WIDTH, HAWK_HEIGHT)
        self.hp = HAWK_HP
        self.active = True
        self.speed_x = HAWK_SPEED * random.choice([-1, 1])
        self.shoot_timer = 60
        self.hit_cooldown = 0

    def update(self, wind: float = 0.0) -> None:
        """Двигаться горизонтально, управлять таймерами стрельбы и неуязвимости."""
        if not self.active:
            return
        self.move(self.speed_x, 0)
        if self.x <= 0 or self.x + self.width >= WIDTH:
            self.speed_x = -self.speed_x
        self.shoot_timer -= 1
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1


# =============================================================================
# Подсистема: очки (SRP — только работа с файлами счёта)
# =============================================================================

class ScoreManager:
    """
    Отвечает исключительно за сохранение и загрузку рекорда и последнего счёта.

    Принцип единственной ответственности (SRP): вся файловая работа
    с очками изолирована здесь и не засоряет GameState.
    """

    _HIGH_SCORE_FILE = "save.txt"
    _LAST_SCORE_FILE = "last_score.txt"

    def load_high_score(self) -> int:
        """Загрузить рекорд с диска. Возвращает 0 при ошибке."""
        try:
            with open(self._HIGH_SCORE_FILE, "r") as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self, score: int, current_high: int) -> int:
        """Сохранить рекорд, если score превышает текущий. Возвращает новый рекорд."""
        if score > current_high:
            try:
                with open(self._HIGH_SCORE_FILE, "w") as f:
                    f.write(str(score))
                return score
            except Exception as e:
                print(f"Ошибка сохранения рекорда: {e}")
        return current_high

    def load_last_score(self) -> int:
        """Загрузить последний счёт с диска. Возвращает 0 при ошибке."""
        try:
            with open(self._LAST_SCORE_FILE, "r") as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0

    def save_last_score(self, score: int) -> None:
        """Сохранить текущий счёт как последний результат."""
        try:
            with open(self._LAST_SCORE_FILE, "w") as f:
                f.write(str(score))
        except Exception as e:
            print(f"Ошибка сохранения счёта: {e}")


# =============================================================================
# Подсистема: уровни (SRP — только конфигурация уровней)
# =============================================================================

class LevelManager:
    """
    Отвечает исключительно за настройку и инициализацию каждого уровня.

    Принцип единственной ответственности (SRP): логика уровней отделена
    от хранения состояния игры.
    """

    def load_level(self, level: int, state: "GameState") -> None:
        """Настроить состояние игры для указанного уровня."""
        state.level = level
        state.animals = []
        state.lightnings = []
        state.birds = []
        state.bird_projectiles = []
        state.hawk_boss = None
        state.hawk_stones = []

        state.balls = [BallModel(), BallModel()] if level >= 5 and len(state.balls) < 2 else [BallModel()]
        for b in state.balls:
            b.reset()

        state.combo_timer = 0
        state.wind_speed = 0.0
        state.wind_timer = 0

        self._configure_environment(level, state)
        self._spawn_animals(level, state)

    def _configure_environment(self, level: int, state: "GameState") -> None:
        """Настроить облака, ветер и босса для данного уровня."""
        if level == 1:
            state.wind_cooldown = -1
            state.clouds = []
        elif level == 2:
            state.wind_cooldown = 1200
            state.clouds = [CloudModel() for _ in range(2)]
        elif level in (3, 4):
            state.wind_cooldown = -1
            state.clouds = []
            if level == 4:
                state.hawk_boss = HawkBossModel()
        elif level == 7:
            state.wind_cooldown = -1
            state.hawk_boss = HawkBossModel()
            state.hawk_boss.hp = HAWK_HP * 2
            state.clouds = []
        else:
            state.wind_cooldown = -1
            state.clouds = [CloudModel() for _ in range(min(2 + level, 5))]

    def _spawn_animals(self, level: int, state: "GameState") -> None:
        """Заполнить сетку зверьков для уровней без босса."""
        if level in (4, 7):
            return
        speed = (BASE_ANIMAL_SPEED + ANIMAL_SPEED_INCREMENT) if level == 3 \
            else (BASE_ANIMAL_SPEED + (level - 1) * ANIMAL_SPEED_INCREMENT)
        if level == 3:
            state.bird_spawn_timer = random.randint(60, 150)
        for row in range(ANIMAL_GRID_ROWS):
            for col in range(ANIMAL_GRID_COLS):
                is_golden = random.random() < GOLDEN_ANIMAL_CHANCE
                x = ANIMAL_START_X + col * ANIMAL_COL_SPACING
                y = ANIMAL_START_Y + row * ANIMAL_ROW_SPACING
                state.animals.append(AnimalModel(x, y, speed, is_golden))


# =============================================================================
# Подсистема: коллизии (SRP — только обнаружение столкновений)
# =============================================================================

class CollisionHandler:
    """
    Отвечает исключительно за обнаружение и обработку коллизий.

    Принцип единственной ответственности (SRP): вся логика столкновений
    изолирована здесь и не загромождает GameState.
    """

    def check(self, state: "GameState") -> None:
        """Выполнить все проверки коллизий за текущий кадр."""
        self._check_ball_missed(state)
        self._check_ball_vs_player(state)
        self._check_ball_vs_birds(state)
        self._check_ball_vs_hawk(state)
        self._check_cloud_shooting(state)
        self._check_lightning_vs_player(state)
        self._check_bird_projectiles_vs_player(state)
        self._check_hawk_stones_vs_player(state)
        self._check_animals(state)
        self._check_level_completion(state)

    # ── Вспомогательный метод (DRY) ──────────────────────────────────────────

    def _hit_player(self, player: PlayerModel, projectile, state: "GameState") -> None:
        """
        Нанести урон игроку: снять жизнь, деактивировать снаряд,
        вызвать Game Over при исчерпании жизней.

        Устраняет дублирование (DRY): этот паттерн использовался 4 раза.
        """
        player.lives -= 1
        projectile.active = False
        if player.lives <= 0:
            state.state = "GAME_OVER"
            state.save_game_results()

    # ── Частные методы проверок ───────────────────────────────────────────────

    def _check_ball_missed(self, state: "GameState") -> None:
        """Снять жизнь, если все мячи упали за экран."""
        if not any(b.active for b in state.balls):
            state.player.lives -= 1
            state.player.combo_count = 0
            if state.player.lives <= 0:
                state.state = "GAME_OVER"
                state.save_game_results()
            else:
                for b in state.balls:
                    b.active = True
                    b.reset()

    def _check_ball_vs_player(self, state: "GameState") -> None:
        """Отразить мячи, попавшие в платформу игрока."""
        p = state.player
        for b in state.balls:
            if not b.active:
                continue
            if b.y + b.radius >= p.y and b.y - b.radius <= p.y + p.height:
                if p.x <= b.x <= p.x + p.width:
                    b.y = p.y - b.radius
                    b.speed_y = -abs(b.speed_y)
                    b.speed_x = ((b.x - p.x) / p.width - 0.5) * 10
            if b.y >= HEIGHT:
                b.active = False

    def _check_ball_vs_birds(self, state: "GameState") -> None:
        """Уничтожить птицу при попадании мяча."""
        for b in state.balls:
            if not b.active:
                continue
            for bird in state.birds:
                if bird.active:
                    dist = math.hypot(b.x - (bird.x + bird.width // 2),
                                      b.y - (bird.y + bird.height // 2))
                    if dist <= b.radius + max(bird.width, bird.height) // 2:
                        bird.active = False
                        b.speed_y = -b.speed_y
                        state.player.score += 30

    def _check_ball_vs_hawk(self, state: "GameState") -> None:
        """Нанести урон боссу-ястребу при попадании мяча."""
        if not (state.hawk_boss and state.hawk_boss.active):
            return
        hb = state.hawk_boss
        for b in state.balls:
            if not b.active:
                continue
            dist = math.hypot(b.x - (hb.x + hb.width // 2),
                              b.y - (hb.y + hb.height // 2))
            if dist <= b.radius + max(hb.width, hb.height) // 2:
                b.speed_y = -b.speed_y
                if hb.hit_cooldown <= 0:
                    hb.hp -= 1
                    hb.hit_cooldown = 30
                    if hb.hp <= 0:
                        hb.active = False
                        state.player.score += 500

    def _check_cloud_shooting(self, state: "GameState") -> None:
        """Создать молнию, если таймер облака истёк."""
        for cloud in state.clouds:
            if cloud.shoot_timer <= 0:
                state.lightnings.append(
                    LightningModel(cloud.x + cloud.width // 2, cloud.y + cloud.height)
                )
                cloud.shoot_timer = random.randint(100, 300)

    def _check_lightning_vs_player(self, state: "GameState") -> None:
        """Поразить игрока молнией и убрать вышедшие за экран."""
        p = state.player
        for lightning in state.lightnings:
            if lightning.active:
                hits = (lightning.y + lightning.height >= p.y and
                        lightning.y <= p.y + p.height and
                        p.x <= lightning.x <= p.x + p.width)
                if hits:
                    self._hit_player(p, lightning, state)
                elif lightning.y > HEIGHT:
                    lightning.active = False
        state.lightnings = [l for l in state.lightnings if l.active]

    def _check_bird_projectiles_vs_player(self, state: "GameState") -> None:
        """Поразить игрока камнем птицы и убрать вышедшие за экран."""
        p = state.player
        for proj in state.bird_projectiles:
            if proj.active:
                hits = (proj.y + proj.height >= p.y and
                        proj.y <= p.y + p.height and
                        p.x <= proj.x <= p.x + p.width)
                if hits:
                    self._hit_player(p, proj, state)
                elif proj.y > HEIGHT:
                    proj.active = False
        state.bird_projectiles = [pr for pr in state.bird_projectiles if pr.active]

    def _check_hawk_stones_vs_player(self, state: "GameState") -> None:
        """Поразить игрока камнем босса и убрать вышедшие за экран."""
        p = state.player
        for stone in state.hawk_stones:
            if stone.active:
                hits = (stone.y + stone.height >= p.y and
                        stone.y <= p.y + p.height and
                        p.x <= stone.x <= p.x + p.width)
                if hits:
                    self._hit_player(p, stone, state)
                elif stone.y > HEIGHT:
                    stone.active = False
        state.hawk_stones = [s for s in state.hawk_stones if s.active]

    def _check_animals(self, state: "GameState") -> None:
        """Обработать коллизии мяча со зверьками и зверьков с платформой."""
        p = state.player
        for animal in state.animals:
            if animal.caught or animal.lost:
                continue
            if not animal.falling:
                for b in state.balls:
                    if b.active and math.hypot(b.x - animal.x, b.y - animal.y) <= b.radius + animal.radius:
                        animal.falling = True
                        b.speed_y = -b.speed_y
            else:
                if (animal.y + animal.radius >= p.y and
                        animal.y - animal.radius <= p.y + p.height and
                        p.x <= animal.x <= p.x + p.width):
                    animal.caught = True
                    if animal.is_golden:
                        p.lives += 1
                    else:
                        p.score += 20
                    p.combo_count += 1
                    if p.combo_count >= 3:
                        p.score += 50
                        p.combo_count = 0
                        state.combo_timer = 60
                elif animal.y - animal.radius > HEIGHT:
                    animal.lost = True
                    p.score = max(0, p.score - 15)

    def _check_level_completion(self, state: "GameState") -> None:
        """Перейти на следующий уровень при выполнении условия победы."""
        if state.state != "PLAYING":
            return
        if state.level in (4, 7):
            complete = state.hawk_boss is not None and not state.hawk_boss.active
        else:
            complete = all(a.caught or a.lost for a in state.animals)
        if complete:
            state.level_manager.load_level(state.level + 1, state)


# =============================================================================
# Главный класс состояния игры
# =============================================================================

class GameState:
    """
    Хранит текущее состояние игры и координирует подсистемы.

    Делегирует ответственности:
      - ScoreManager    — работа с файлами очков
      - LevelManager    — загрузка и конфигурация уровней
      - CollisionHandler — обнаружение коллизий
    """

    def __init__(self):
        # Подсистемы
        self.score_manager = ScoreManager()
        self.level_manager = LevelManager()
        self._collision_handler = CollisionHandler()

        # Сущности
        self.player = PlayerModel()
        self.balls = [BallModel()]
        self.animals = []
        self.clouds = []
        self.lightnings = []
        self.birds = []
        self.bird_projectiles = []
        self.hawk_boss = None
        self.hawk_stones = []

        # Игровые переменные
        self.level = 1
        self.combo_timer = 0
        self.wind_speed = 0.0
        self.wind_timer = 0
        self.wind_cooldown = 0
        self.bird_spawn_timer = random.randint(300, 600)
        self.state = "MENU"
        self.paused = False

        # Очки
        self.high_score = self.score_manager.load_high_score()
        self.last_score = self.score_manager.load_last_score()

        self.level_manager.load_level(1, self)

    def save_game_results(self) -> None:
        """Сохранить результаты текущей игры на диск."""
        self.last_score = self.player.score
        self.score_manager.save_last_score(self.last_score)
        self.high_score = self.score_manager.save_high_score(self.player.score, self.high_score)

    def update(self) -> None:
        """Обновить состояние всех игровых объектов за один кадр."""
        if self.state != "PLAYING" or self.paused:
            return

        if self.combo_timer > 0:
            self.combo_timer -= 1

        self._update_wind()

        for b in self.balls:
            b.update(self.wind_speed)
        for cloud in self.clouds:
            cloud.update(self.wind_speed)
        for lightning in self.lightnings:
            lightning.update(self.wind_speed)
        for animal in self.animals:
            animal.update(self.wind_speed)

        self._update_birds()

        if self.hawk_boss and self.hawk_boss.active:
            self.hawk_boss.update(self.wind_speed)
            if self.hawk_boss.shoot_timer <= 0:
                self.hawk_stones.append(
                    HawkStoneModel(self.hawk_boss.x + self.hawk_boss.width // 2,
                                   self.hawk_boss.y + self.hawk_boss.height)
                )
                self.hawk_boss.shoot_timer = random.randint(40, 90)

        for stone in self.hawk_stones:
            stone.update(self.wind_speed)

        self._collision_handler.check(self)

    def _update_wind(self) -> None:
        """Обновить скорость и таймеры ветра."""
        if self.wind_timer > 0:
            self.wind_timer -= 1
            if self.wind_timer <= 0:
                self.wind_speed = 0.0
                if self.level == 2:
                    self.wind_cooldown = 1200
        elif self.wind_cooldown > 0:
            self.wind_cooldown -= 1
        elif self.wind_cooldown == 0 and self.level == 2:
            self.wind_speed = random.choice([-2.0, 2.0]) * random.uniform(0.5, 1.5)
            self.wind_timer = random.randint(120, 240)

    def _update_birds(self) -> None:
        """Обновить птиц и их снаряды; управлять спавном."""
        spawn = (self.level == 3) or (self.level not in (1, 2, 4, 7))
        if spawn:
            self.bird_spawn_timer -= 1
            if self.bird_spawn_timer <= 0:
                self.birds.append(BirdModel())
                interval = random.randint(80, 160) if self.level == 3 else random.randint(400, 800)
                self.bird_spawn_timer = interval

        for bird in self.birds:
            bird.update(self.wind_speed)
            if bird.active and bird.shoot_timer <= 0:
                self.bird_projectiles.append(
                    BirdProjectileModel(bird.x + bird.width // 2, bird.y + bird.height)
                )
                bird.shoot_timer = random.randint(60, 150)
        self.birds = [b for b in self.birds if b.active]

        for proj in self.bird_projectiles:
            proj.update(self.wind_speed)
