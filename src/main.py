import esper
import utils
import pygame
import pygame_gui

from animation import (
    FrameCyclingProcessor,
    StateChangingProcessor,
    StateHandlingProcessor,
)
from event import EventProcessor
from utils import FPS, RESOLUTION
from ui import UiDrawingProcessor
from creature import PlayerMarker
from camera import CameraProcessor
from render import RenderProcessor
from roof import RoofTogglingProcessor
from chrono import DayNightCyclingProcessor
from object import SolidGroup, SolidGroupingProcessor
from movement import MovementProcessor, RotationProcessor
from location import Location, InitLocationProcessor, Position
from chunk import ChunkUnloadingProcessor, ChunkLoadingProcessor


PROCESSORS = (
    EventProcessor,
    InitLocationProcessor,
    SolidGroupingProcessor,
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
    solid_group = world.create_entity(SolidGroup())
    player = utils.creature(
        world,
        "player",
        Position(location, "test", pygame.Vector2(320, 320)),
        PlayerMarker(),
        extra_parts={"legs"},
        surface_preprocessor=lambda s: pygame.transform.rotate(
            pygame.transform.scale2x(s), 90
        ),
    )


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
