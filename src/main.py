import sys
import esper
import utils
import pygame
import pygame_gui

from copy import deepcopy
from utils.consts import FPS

from movement import (
    DirectionAngleCalculationProcessor,
    MovementProcessor,
    RotationProcessor,
    Velocity,
)
from animation import (
    FrameCyclingProcessor,
    StateChangingProcessor,
    StateHandlingProcessor,
)
from location import (
    InitLocationProcessor,
    LocationInitRequest,
    SpawnPoint,
    SpawnablePositioningProcessor,
)
from menu import (
    MenuDrawingProcessor,
    MenuUpdatingProcessor,
    MenuTogglingProcessor,
    MenuCreationProcessor,
)
from event import EventProcessor
from bind import BindingProcessor
from ui import UiDrawingProcessor
from camera import CameraProcessor
from render import RenderProcessor
from roof import RoofTogglingProcessor
from ai import (
    Enemy,
    EnemyRoutingProcessor,
    EnemyRotationProcessor,
    InstructingProcessor,
)
from chrono import DayNightCyclingProcessor
from creature import PlayerMarker, ZombieMarker
from chunk import ChunkUnloadingProcessor, ChunkLoadingProcessor
from object import SolidGroup, SolidGroupingProcessor, BumpMarkerRemovingProcessor


PROCESSORS = (
    EventProcessor,
    InitLocationProcessor,
    SpawnablePositioningProcessor,
    BindingProcessor,
    SolidGroupingProcessor,
    DirectionAngleCalculationProcessor,
    RotationProcessor,
    MovementProcessor,
    FrameCyclingProcessor,
    StateChangingProcessor,
    StateHandlingProcessor,
    CameraProcessor,
    RoofTogglingProcessor,
    EnemyRoutingProcessor,
    EnemyRotationProcessor,
    InstructingProcessor,
    RenderProcessor,
    BumpMarkerRemovingProcessor,
    DayNightCyclingProcessor,
    UiDrawingProcessor,
)

CHUNK_LOADER_PROCESSORS = (
    ChunkUnloadingProcessor,
    ChunkLoadingProcessor,
)

MENU_MANAGER_PROCESSORS = (
    MenuCreationProcessor,
    MenuTogglingProcessor,
    MenuUpdatingProcessor,
    MenuDrawingProcessor,
)


def fill_world(world: esper.World):
    world.create_entity(LocationInitRequest("test"))

    sprite_groups = world.create_entity(SolidGroup())
    player = utils.make.creature(
        world,
        "player",
        SpawnPoint("player"),
        PlayerMarker(),
        extra_parts={"legs"},
        surface_preprocessor=lambda s: pygame.transform.rotate(
            pygame.transform.scale2x(s), 90
        ),
    )
    zombie = utils.make.creature(
        world,
        "zombie",
        SpawnPoint("zombie"),
        Velocity(pygame.Vector2(0), 5),
        Enemy(player),
        ZombieMarker(),
        surface_preprocessor=lambda s: pygame.transform.rotate(s, -90),
    )


if __name__ == "__main__":
    settings = deepcopy(utils.consts.DEFAULT_SETTINGS)

    pygame.init()
    screen = pygame.display.set_mode(settings["resolution"])
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

    menumanager = esper.World()
    for processor in MENU_MANAGER_PROCESSORS:
        menumanager.add_processor(processor())

    running = [True]
    paused = [False]
    started = [True if "--debug" in sys.argv else False]
    current_menu = ["main_menu"]

    while running[0]:
        events = pygame.event.get()

        menumanager.process(
            current_menu=current_menu,
            screen=screen,
            settings=settings,
            events=events,
            paused=paused,
            started=started,
        )

        if not started[0] or paused[0]:
            pygame.display.flip()
            continue

        world.process(
            screen=screen,
            paused=paused,
            events=events,
            running=running,
            settings=settings,
            dt=clock.tick(FPS),
            uimanager=uimanager,
        )
        chunkloader.process(settings["resolution"], world)

        pygame.display.flip()

    pygame.quit()
