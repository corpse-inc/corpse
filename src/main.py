import esper
import pygame

from input import *
from render import *
from creature import *
from movement import *
from location import *
from animation import *
from utils import FPS, RESOLUTION, ResourcePath


PROCESSORS = (
    InputProcessor,
    InitLocationProcessor,
    MovementProcessor,
    RenderProcessor,
    FrameCyclingProcessor,
)


def fill_world(world: esper.World):
    location = world.create_entity(Location())
    player = world.create_entity(
        PlayerMarker(),
        Creature(),
        Animation(
            state=(AnimationState.Stands,),
            frames={
                (AnimationState.Stands,): (
                    pygame.image.load(
                        ResourcePath.creature_frame("player", AnimationState.Stands, 1)
                    ).convert_alpha(),
                ),
            },
        ),
        Velocity(pygame.Vector2(0, 0)),
        Position(location, "summer_island", pygame.Vector2(320, 320)),
        Renderable(),
    )


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(RESOLUTION)
    pygame.display.set_caption("Corpse inc.")
    clock = pygame.time.Clock()

    world = esper.World()

    fill_world(world)

    for processor in PROCESSORS:
        world.add_processor(processor())

    running = [True]
    while running[0]:
        world.process(clock.tick(FPS), screen, running)

    pygame.quit()
