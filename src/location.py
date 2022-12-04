import pygame
import esper
import pytmx
import pyscroll
import utils

from enum import Enum, IntEnum, auto
from dataclasses import dataclass as component

from creature import PlayerMarker
from render import Renderable
from object import Size, Solid


class Layer(IntEnum):
    """Каждая локация имеет три слоя: земля, объекты и крыши. На земле
    расположены тайлы травы, дорог и т. п. На слое объектов расположены все
    существа, объекты и предметы. На слое с крышами расположены крыши строений."""

    # Порядок имеет значение!
    Ground = auto()
    Objects = auto()
    Creatures = auto()
    Roofs = auto()

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, s: str):
        return cls[utils.snake_to_camel_case(s)]


@component
class Location:
    map: pytmx.TiledMap | None = None
    sprites: pyscroll.PyscrollGroup | None = None
    renderer: pyscroll.BufferedRenderer | None = None


class PointAnchor(Enum):
    TopLeft = auto()
    Center = auto()


@component
class Position:
    location: int
    location_id: str
    coords: pygame.Vector2
    layer: Layer = Layer.Objects
    anchor: PointAnchor = PointAnchor.Center


@component
class SkipLocationInitMarker:
    """Если в мире игры есть сущность с данным компонентом, значит нужно
    пропустить инициализацию локаций."""


class InitLocationProcessor(esper.Processor):
    """Инициализирует локацию, на которой в данный момент находится игрок."""

    def _fill_objects(self, tilemap: pytmx.TiledMap, location: int, location_id: str):
        from movement import Direction

        for group in tilemap.objectgroups:
            for object in group:
                object: pytmx.TiledObject

                entity = self.world.create_entity(
                    Position(
                        location,
                        location_id,
                        pygame.Vector2(object.as_points[0]),
                        Layer.from_str(group.name),
                        PointAnchor.TopLeft,
                    ),
                    Size(object.width, object.height),
                    Renderable(),
                )

                if object.image is not None:
                    self.world.add_component(
                        entity, utils.animation_from_surface(object.image)
                    )

                if object.rotation != 0:
                    self.world.add_component(
                        entity,
                        Direction(angle=object.rotation),
                    )

                if object.properties.get("is_solid", False):
                    self.world.add_component(entity, Solid())

    def _make_location_data(self, location: int, location_id: str):
        tilemap = pytmx.load_pygame(utils.ResourcePath.location_tilemap(location_id))

        self._fill_objects(tilemap, location, location_id)

        renderer = pyscroll.BufferedRenderer(
            data=pyscroll.TiledMapData(tilemap),
            size=utils.CAMERA_SIZE,
            zoom=utils.CAMERA_ZOOM,
        )

        sprites = pyscroll.PyscrollGroup(map_layer=renderer)

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
