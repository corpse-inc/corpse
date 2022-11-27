import esper
import pygame

FPS = 60
RESOLUTION = 720, 480


class Game:
    def __init__(self, window, world=None):
        self.window = window
        self.world = world

    def init_world(self):
        world = esper.World()

        return world

    def tick(self):
        self.clock.tick_busy_loop(FPS)

    def run(self):
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(1, 1)

        if self.world is None:
            self.init_world()

        running = True
        while running:
            self.tick()


if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode(RESOLUTION)
    pygame.display.set_caption("Corpse inc.")

    Game(window).run()

    pygame.quit()
