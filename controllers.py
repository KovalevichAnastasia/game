import pygame

class GameController:
    def __init__(self, game_state):
        self.game_state = game_state

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.game_state.state == "MENU":
                    if event.key == pygame.K_SPACE:
                        self.game_state.__init__()
                        self.game_state.state = "PLAYING"
                elif self.game_state.state in ["GAME_OVER", "WIN"]:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state.state = "MENU"

        keys = pygame.key.get_pressed()
        if self.game_state.state == "PLAYING":
            if keys[pygame.K_LEFT]:
                self.game_state.player.move_left()
            if keys[pygame.K_RIGHT]:
                self.game_state.player.move_right()

        return True
