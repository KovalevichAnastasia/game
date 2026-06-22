import pygame

class GameController:

    def __init__(self, game_state):
        self._game_state = game_state

    def handle_events(self) -> bool:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)

        self._handle_movement()
        return True

    def _handle_keydown(self, key: int) -> None:

        state = self._game_state

        if state.state == "MENU":
            if key == pygame.K_SPACE:
                state.__init__()
                state.state = "PLAYING"

        elif state.state == "PLAYING":
            if key == pygame.K_p:
                state.paused = not state.paused

        elif state.state in ("GAME_OVER", "WIN"):
            if key == pygame.K_ESCAPE:
                state.state = "MENU"

    def _handle_movement(self) -> None:

        state = self._game_state
        if state.state != "PLAYING" or state.paused:
            return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            state.player.move_left()
        if keys[pygame.K_RIGHT]:
            state.player.move_right()

