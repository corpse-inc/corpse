import pygame
import esper
import pytmx
import pyscroll
import utils

from dataclasses import dataclass as component
from enum import Enum

from creature import PlayerMarker


class Layer(Enum):
    """Каждая локация имеет три слоя: земля, объекты и крыши. На земле
    расположены тайлы травы, дорог и т. п. На слое объектов расположены все
    существа, объекты и предметы. На слое с крышами расположены крыши строений."""

    # Порядок имеет значение!
    Ground = 0
    Objects = 1
    Roofs = 2


@component
class Location:
    map: pytmx.TiledMap | None = None
    sprites: pyscroll.PyscrollGroup | None = None


@component
class Position:
    location: int
    location_id: str
    coords: pygame.math.Vector2
    layer: Layer = Layer.Objects


@component
class SkipLocationInitMarker:
    """Если в мире игры есть сущность с данным компонентом, значит нужно
    пропустить инициализацию локаций."""


class InitLocationProcessor(esper.Processor):
    """Инициализирует локацию, на которой в данный момент находится игрок."""

    def _make_map_and_scroll_group(self, location_id: str):
        tmx_data = pytmx.load_pygame(utils.ResourcePath.location_tilemap(location_id))

        map_layer = pyscroll.BufferedRenderer(
            data=pyscroll.TiledMapData(tmx_data),
            size=utils.RESOLUTION,
        )

        return tmx_data, pyscroll.PyscrollGroup(map_layer=map_layer)

    def process(self, dt, screen, running):
        if len(self.world.get_component(SkipLocationInitMarker)) != 0:
            return

        for _, (_, position) in self.world.get_components(PlayerMarker, Position):
            location = self.world.component_for_entity(position.location, Location)
            location.map, location.sprites = self._make_map_and_scroll_group(
                position.location_id
            )
            self.world.create_entity(SkipLocationInitMarker())
