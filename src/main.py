import sys
import esper
import utils
import pygame
import pygame_gui
import pygame_menu

from typing import Dict
from copy import deepcopy
from utils.consts import FPS

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
from event import EventProcessor
from bind import BindingProcessor
from ui import UiDrawingProcessor
from creature import PlayerMarker
from camera import CameraProcessor
from render import RenderProcessor
from roof import RoofTogglingProcessor
from chrono import DayNightCyclingProcessor
from object import SolidGroup, SolidGroupingProcessor
from movement import MovementProcessor, RotationProcessor
from chunk import ChunkUnloadingProcessor, ChunkLoadingProcessor

PROCESSORS = (
    EventProcessor,
    InitLocationProcessor,
    SpawnablePositioningProcessor,
    BindingProcessor,
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


def run(screen: pygame.surface.Surface, settings: Dict):
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
        world.process(
            screen=screen,
            running=running,
            settings=settings,
            dt=clock.tick(FPS),
            uimanager=uimanager,
        )
        chunkloader.process(settings["resolution"], world)
        pygame.display.flip()


if __name__ == "__main__":
    settings = deepcopy(utils.consts.DEFAULT_SETTINGS)

    pygame.init()
    screen = pygame.display.set_mode(settings["resolution"])
    pygame.display.set_caption("Corpse inc.")

    if "--debug" in sys.argv:
        run(screen, settings)
    else:

        def apply_settings():
            pygame.display.set_mode(settings["resolution"])

        settings_menu = pygame_menu.Menu(
            "Corpse inc. -> Settings",
            *settings["resolution"],
            theme=utils.make.settings_menu_theme(),
            onreset=apply_settings,
        )

        def change_resolution(_, res):
            settings["resolution"] = res

        settings_menu.add.dropselect(
            "Разрешение экрана",
            [("640x480", (640, 480)), ("720x480", (720, 480))],
            onchange=change_resolution,
        )

        menu = pygame_menu.Menu(
            "Corpse inc.",
            *settings["resolution"],
            center_content=False,
            theme=utils.make.main_menu_theme(),
        )

        menu.add.button("Играть", lambda: run(screen, settings))
        menu.add.button("Настройки", settings_menu)
        menu.add.button("Выйти", pygame_menu.events.EXIT)

        menu.mainloop(screen)

    pygame.quit()
