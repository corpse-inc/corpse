import pygame
import esper
import pytmx
import pyscroll

from render import Renderable
import utils

from dataclasses import dataclass as component
from enum import IntEnum

from creature import PlayerMarker


class Layer(IntEnum):
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
    renderer: pyscroll.BufferedRenderer | None = None


@component
class Position:
    location: int
    location_id: str
    coords: pygame.Vector2
    layer: Layer = Layer.Objects


@component
class SkipLocationInitMarker:
    """Если в мире игры есть сущность с данным компонентом, значит нужно
    пропустить инициализацию локаций."""


class InitLocationProcessor(esper.Processor):
    """Инициализирует локацию, на которой в данный момент находится игрок."""

    def _make_location_data(self, location: int, location_id: str):
        tilemap = pytmx.load_pygame(utils.ResourcePath.location_tilemap(location_id))

        renderer = pyscroll.BufferedRenderer(
            data=pyscroll.TiledMapData(tilemap),
            size=utils.CAMERA_SIZE,
            zoom=utils.CAMERA_ZOOM,
        )

        sprites = pyscroll.PyscrollGroup(map_layer=renderer)

        for object in tilemap.layers[Layer.Roofs]:
            object: pytmx.TiledObject

            points = object.as_points
            point = (
                sum(map(lambda p: p.x, points)) / len(points),
                sum(map(lambda p: p.y, points)) / len(points),
            )

            entity = self.world.create_entity(
                Position(location, location_id, pygame.Vector2(point)),
                Renderable(),
            )

            if object.image is not None:
                image = pygame.transform.rotate(object.image, -object.rotation)
                self.world.add_component(entity, utils.animation_from_surface(image))

        return tilemap, sprites, renderer

    def process(self, **_):
        if len(self.world.get_component(SkipLocationInitMarker)) != 0:
            return

        for _, (_, position) in self.world.get_components(PlayerMarker, Position):
            location = self.world.component_for_entity(position.location, Location)
            (
                location.map,
                location.sprites,
                location.renderer,
            ) = self._make_location_data(position.location, position.location_id)
            self.world.create_entity(SkipLocationInitMarker())
