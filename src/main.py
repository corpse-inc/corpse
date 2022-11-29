import esper
import pygame

from input import InputProcessor
from movement import MovementProcessor
from location import LocationProcessor, PositionProcessor

FPS = 60
RESOLUTION = 720, 480

PROCESSORS = (
    InputProcessor,
    LocationProcessor,
    MovementProcessor,
    PositionProcessor,
)


if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode(RESOLUTION)
    pygame.display.set_caption("Corpse inc.")
    clock = pygame.time.Clock()

    world = esper.World()

    for processor in PROCESSORS:
        world.add_processor(processor())

    running = [True]
    while running[0]:
        world.process(clock.tick(FPS), running)

    pygame.quit()
