import pygame
from constants import WIDTH, HEIGHT, FPS
from models import GameState
from views import GameView
from controllers import GameController

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Пушистый переполох")
    clock = pygame.time.Clock()

    game_state = GameState()
    view = GameView(screen)
    controller = GameController(game_state)

    running = True
    while running:
        running = controller.handle_events()
        game_state.update()
        view.draw(game_state)

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
