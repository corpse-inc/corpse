import esper
import pygame

from chunk import ChunkUnloadingProcessor, ChunkLoadingProcessor
from roof import RoofTogglingProcessor
from input import InputProcessor
from camera import CameraProcessor
from render import RenderProcessor, Renderable
from creature import Creature, PlayerMarker
from movement import MovementProcessor, RotationProcessor, Velocity
from location import Location, InitLocationProcessor, Position
from animation import Animation, AnimationState, FrameCyclingProcessor
from utils import FPS, RESOLUTION, ResourcePath


PROCESSORS = (
    InputProcessor,
    InitLocationProcessor,
    MovementProcessor,
    RotationProcessor,
    FrameCyclingProcessor,
    CameraProcessor,
    RoofTogglingProcessor,
    RenderProcessor,
)

CHUNK_LOADER_PROCESSORS = (
    ChunkUnloadingProcessor,
    ChunkLoadingProcessor,
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
                    pygame.transform.rotate(
                        pygame.transform.scale2x(
                            pygame.image.load(
                                ResourcePath.creature_frame(
                                    "player", AnimationState.Stands, 1
                                )
                            ).convert_alpha()
                        ),
                        90,
                    ),
                ),
            },
        ),
        Velocity(pygame.Vector2(0, 0)),
        Position(location, "test", pygame.Vector2(320, 320)),
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

    chunkloader = esper.World()

    for processor in CHUNK_LOADER_PROCESSORS:
        chunkloader.add_processor(processor())

    running = [True]
    while running[0]:
        chunkloader.process(RESOLUTION, world)
        world.process(dt=clock.tick(FPS), screen=screen, running=running)

    pygame.quit()
