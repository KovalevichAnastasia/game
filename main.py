import pygame
from constants import WIDTH, HEIGHT, FPS
from models import GameState
from views import GameView
from controllers import GameController


def main() -> None:
    """Инициализировать игру и запустить основной цикл."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Пушистый переполох")
    clock = pygame.time.Clock()

    try:
        pygame.mixer.init()
        pygame.mixer.music.load("assets/Morning_at_the_Summit.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"Аудио недоступно, игра запускается без звука: {e}")

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
