# =============================================================================
# constants.py — Все игровые константы и настройки
# =============================================================================

# Настройки экрана
WIDTH = 800
HEIGHT = 600
FPS = 60

# Цвета (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (135, 206, 235)
DARK_BLUE = (25, 25, 112)
GREEN = (34, 139, 34)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
GRAY = (169, 169, 169)

# Игрок
PLAYER_WIDTH = 120
PLAYER_HEIGHT = 20
PLAYER_SPEED = 7
PLAYER_LIVES = 10

# Мяч
BALL_RADIUS = 12
BALL_SPEED_X = 4
BALL_SPEED_Y = 4

# Птица-враг
BIRD_WIDTH = 100
BIRD_HEIGHT = 100
BIRD_SPEED = 3
BIRD_PROJECTILE_RADIUS = 14
BIRD_PROJECTILE_SPEED = 5

# Босс-ястреб
HAWK_WIDTH = 200
HAWK_HEIGHT = 200
HAWK_SPEED = 2
HAWK_HP = 6
HAWK_STONE_RADIUS = 8
HAWK_STONE_SPEED = 6

# Зверёк
ANIMAL_RADIUS = 30
GOLDEN_ANIMAL_CHANCE = 0.1  # Вероятность золотого зверька

# Сетка зверьков
ANIMAL_GRID_ROWS = 3
ANIMAL_GRID_COLS = 8
ANIMAL_START_X = 100
ANIMAL_START_Y = 150
ANIMAL_COL_SPACING = 80
ANIMAL_ROW_SPACING = 60

# Скорость зверьков (прогрессия по уровням)
BASE_ANIMAL_SPEED = 3.0
ANIMAL_SPEED_INCREMENT = 1.5

# Облако
CLOUD_WIDTH = 80
CLOUD_HEIGHT = 40
CLOUD_SPEED = 2

# Молния
LIGHTNING_WIDTH = 5
LIGHTNING_HEIGHT = 20
LIGHTNING_SPEED = 5
