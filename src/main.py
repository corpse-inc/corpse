import esper
import pygame
import pygame_gui

from animation import (
    Part,
    States,
    PartType,
    StateType,
    Animation,
    FrameCyclingProcessor,
    StateChangingProcessor,
    StateHandlingProcessor,
)
from input import InputProcessor
from camera import CameraProcessor
from roof import RoofTogglingProcessor
from chrono import DayNightCyclingProcessor
from creature import Creature, PlayerMarker
from render import RenderProcessor, Renderable
from utils import FPS, RESOLUTION, ResourcePath
from location import Location, InitLocationProcessor, Position
from chunk import ChunkUnloadingProcessor, ChunkLoadingProcessor
from ui import UiDrawingProcessor
from movement import Direction, MovementProcessor, RotationProcessor, Velocity


PROCESSORS = (
    InputProcessor,
    InitLocationProcessor,
    MovementProcessor,
    RotationProcessor,
    FrameCyclingProcessor,
    StateChangingProcessor,
    StateHandlingProcessor,
    CameraProcessor,
    RoofTogglingProcessor,
    RenderProcessor,
    DayNightCyclingProcessor,
    UiDrawingProcessor,
)

CHUNK_LOADER_PROCESSORS = (
    ChunkUnloadingProcessor,
    ChunkLoadingProcessor,
)


def fill_world(world: esper.World):
    location = world.create_entity(Location())
    player_surface = pygame.transform.rotate(
        pygame.transform.scale2x(
            pygame.image.load(ResourcePath.frame("player", 1, "body")).convert_alpha()
        ),
        90,
    )
    legs_frames = []
    for i in range(1, 8):
        img = pygame.transform.rotate(
            pygame.transform.scale2x(
                pygame.image.load(
                    ResourcePath.frame("player", i, "legs")
                ).convert_alpha()
            ),
            90,
        )
        legs_frames.append(img)

    player = world.create_entity(
        PlayerMarker(),
        Creature(),
        States({StateType.Stands}),
        Animation((player_surface,)),
        Velocity(pygame.Vector2(0, 0)),
        Position(location, "test", pygame.Vector2(320, 320)),
        Direction(),
        Renderable(),
    )
    player_legs = world.create_entity(
        world.component_for_entity(player, Position),
        world.component_for_entity(player, Direction),
        Animation(tuple(legs_frames), 50),
        Renderable(),
        Part(player, PartType.Legs),
    )
    world.component_for_entity(player, Animation).children = (player_legs,)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(RESOLUTION)
    pygame.display.set_caption("Corpse inc.")
    clock = pygame.time.Clock()
    uimanager = pygame_gui.UIManager(screen.get_size())

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
        world.process(
            dt=clock.tick(FPS), screen=screen, uimanager=uimanager, running=running
        )
        pygame.display.flip()

    pygame.quit()
