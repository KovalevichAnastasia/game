import unittest
from models import PlayerModel, BallModel, GameState

class TestGameLogic(unittest.TestCase):
    
    def test_player_movement(self):
        player = PlayerModel()
        initial_x = player.x
        player.move_left()
        self.assertEqual(player.x, initial_x - player.speed)

    def test_player_boundaries(self):
        player = PlayerModel()
        player.x = 0
        player.move_left()
        self.assertEqual(player.x, 0) # Не должен выходить за экран

    def test_game_state_initialization(self):
        game = GameState()
        self.assertEqual(game.state, "MENU")
        self.assertEqual(len(game.animals), 24) # 3 ряда по 8
        self.assertEqual(game.player.lives, 10)
        self.assertEqual(len(game.clouds), 0) # На первом уровне нет тучек
        self.assertTrue(hasattr(game, 'last_score'))

    def test_save_game_results(self):
        game = GameState()
        game.player.score = 50
        game.save_game_results()
        self.assertEqual(game.last_score, 50)
        
        # Проверяем, что при новой инициализации загружается правильный предыдущий счет
        new_game = GameState()
        self.assertEqual(new_game.last_score, 50)

    def test_miss_animal_loses_score(self):
        game = GameState()
        game.state = "PLAYING"
        initial_score = 50
        game.player.score = initial_score
        
        # Находим одного зверька, переводим в состояние падения и опускаем ниже экрана
        animal = game.animals[0]
        animal.falling = True
        animal.y = 700 # Высота экрана HEIGHT = 600
        
        game.check_collisions()
        
        self.assertEqual(game.player.score, max(0, initial_score - 15))
        self.assertTrue(animal.lost)

    def test_lightning_hit_loses_life(self):
        from models import LightningModel
        game = GameState()
        game.state = "PLAYING"
        initial_lives = game.player.lives
        
        p = game.player
        # Размещаем молнию прямо на игрока
        lightning = LightningModel(p.x + p.width // 2, p.y)
        game.lightnings.append(lightning)
        
        game.check_collisions()
        
        self.assertEqual(game.player.lives, initial_lives - 1)
        self.assertFalse(lightning.active)

    def test_ball_reset(self):
        ball = BallModel()
        ball.x = 10
        ball.y = 10
        ball.reset()
        # Должен вернуться в центр экрана по Y
        self.assertEqual(ball.y, 600 // 2)

if __name__ == '__main__':
    unittest.main()
