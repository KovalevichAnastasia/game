import unittest
from models import PlayerModel, BallModel, GameState, ScoreManager, LevelManager

class TestPlayerModel(unittest.TestCase):

    def test_player_movement_left(self):

        player = PlayerModel()
        initial_x = player.x
        player.move_left()
        self.assertEqual(player.x, initial_x - player.speed)

    def test_player_boundary_left(self):

        player = PlayerModel()
        player.x = 0
        player.move_left()
        self.assertEqual(player.x, 0)

    def test_player_boundary_right(self):

        from constants import WIDTH, PLAYER_WIDTH
        player = PlayerModel()
        player.x = WIDTH - PLAYER_WIDTH
        player.move_right()
        self.assertEqual(player.x, WIDTH - PLAYER_WIDTH)

class TestBallModel(unittest.TestCase):

    def test_ball_reset_position(self):

        from constants import WIDTH, HEIGHT
        ball = BallModel()
        ball.x = 10
        ball.y = 10
        ball.reset()
        self.assertEqual(ball.x, WIDTH // 2)
        self.assertEqual(ball.y, HEIGHT // 2)

    def test_ball_reset_speed(self):

        ball = BallModel()
        ball.speed_x = 5
        ball.reset()
        self.assertEqual(ball.speed_x, 0)

class TestGameState(unittest.TestCase):

    def test_initial_state_is_menu(self):

        game = GameState()
        self.assertEqual(game.state, "MENU")

    def test_initial_animals_count(self):

        game = GameState()
        self.assertEqual(len(game.animals), 24)

    def test_initial_lives(self):

        from constants import PLAYER_LIVES
        game = GameState()
        self.assertEqual(game.player.lives, PLAYER_LIVES)

    def test_no_clouds_on_level_1(self):

        game = GameState()
        self.assertEqual(len(game.clouds), 0)

    def test_last_score_attribute_exists(self):

        game = GameState()
        self.assertTrue(hasattr(game, 'last_score'))

    def test_paused_attribute_exists(self):

        game = GameState()
        self.assertFalse(game.paused)

class TestScoreManager(unittest.TestCase):

    def test_save_and_load_last_score(self):

        manager = ScoreManager()
        manager.save_last_score(42)
        self.assertEqual(manager.load_last_score(), 42)

    def test_save_high_score_updates_when_greater(self):

        manager = ScoreManager()
        new_high = manager.save_high_score(9999, 0)
        self.assertEqual(new_high, 9999)

    def test_save_high_score_no_update_when_lower(self):

        manager = ScoreManager()
        result = manager.save_high_score(5, 100)
        self.assertEqual(result, 100)

class TestLevelManager(unittest.TestCase):

    def test_level_4_spawns_hawk_boss(self):

        game = GameState()
        game.level_manager.load_level(4, game)
        self.assertIsNotNone(game.hawk_boss)
        self.assertTrue(game.hawk_boss.active)

    def test_level_4_has_no_animals(self):

        game = GameState()
        game.level_manager.load_level(4, game)
        self.assertEqual(len(game.animals), 0)

    def test_level_2_has_clouds(self):

        game = GameState()
        game.level_manager.load_level(2, game)
        self.assertGreater(len(game.clouds), 0)

    def test_level_5_has_two_balls(self):

        game = GameState()
        game.level_manager.load_level(5, game)
        self.assertEqual(len(game.balls), 2)

class TestCollisions(unittest.TestCase):

    def test_miss_animal_loses_score(self):

        game = GameState()
        game.state = "PLAYING"
        game.player.score = 50
        animal = game.animals[0]
        animal.falling = True
        animal.y = 700
        game._collision_handler.check(game)
        self.assertEqual(game.player.score, 35)
        self.assertTrue(animal.lost)

    def test_lightning_hit_loses_life(self):

        from models import LightningModel
        game = GameState()
        game.state = "PLAYING"
        initial_lives = game.player.lives
        p = game.player
        lightning = LightningModel(p.x + p.width // 2, p.y)
        game.lightnings.append(lightning)
        game._collision_handler.check(game)
        self.assertEqual(game.player.lives, initial_lives - 1)
        self.assertFalse(lightning.active)

    def test_save_game_results(self):

        game = GameState()
        game.player.score = 77
        game.save_game_results()
        self.assertEqual(game.last_score, 77)
        new_game = GameState()
        self.assertEqual(new_game.last_score, 77)

if __name__ == '__main__':
    unittest.main()

