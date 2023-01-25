import pygame
import esper
import pytmx
import pyscroll
import utils

from typing import Tuple
from copy import deepcopy
from enum import IntEnum, auto
from dataclasses import dataclass as component


class Layer(IntEnum):
    """Каждая локация имеет три слоя: земля, объекты и крыши. На земле
    расположены тайлы травы, дорог и т. п. На слое объектов расположены все
    существа, объекты и предметы. На слое с крышами расположены крыши строений."""

    # Порядок имеет значение!
    Ground = auto()
    Items = auto()
    Creatures = auto()
    Objects = auto()
    Roofs = auto()

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, s: str):
        return cls[utils.convert.snake_to_camel_case(s)]


@component
class Location:
    map: pytmx.TiledMap
    renderer: pyscroll.BufferedRenderer
    sprites: pyscroll.PyscrollGroup


@component
class LocationInitRequest:
    """Запрос на инициализацию локации. id - строковый идентификатор
    локации для нахождения её .tmx файла."""

    id: str


@component
class Position:
    location: int
    coords: pygame.Vector2
    layer: Layer = Layer.Objects


@component
class SpawnPoint:
    name: str


class InitLocationProcessor(esper.Processor):
    """Инициализирует локации."""

    def _fill_object(
        self, group: pytmx.TiledObjectGroup, object: pytmx.TiledObject, location: int
    ):
        from roof import Roof
        from movement import Direction
        from render import MakeRenderableRequest
        from object import Invisible, Size, Solid
        from utils.consts import DEFAULT_CONSUME_IMAGE
        from creature import CREATURES, CreatureNotFoundError

        layer = Layer.from_str(group.name)
        position = Position(location, pygame.Vector2(object.as_points[1]), layer)
        size = Size(object.width, object.height)
        image = object.image.convert_alpha() if object.image else None

        match layer:
            case Layer.Items | Layer.Objects | Layer.Roofs:
                entity = self.world.create_entity(
                    position,
                    size,
                    MakeRenderableRequest(),
                )

                if layer == Layer.Roofs:
                    self.world.add_component(entity, Roof())

                if not object.visible:
                    self.world.add_component(entity, Invisible())

                if image and (
                    consume_image := object.properties.get(
                        "consume_image", DEFAULT_CONSUME_IMAGE
                    )
                    or layer == Layer.Objects
                ):
                    image = pygame.transform.scale(image, (object.width, object.height))
                    self.world.add_component(
                        entity,
                        utils.convert.animation_from_surface(image),
                    )

                if object.rotation != 0:
                    self.world.add_component(
                        entity,
                        Direction(angle=object.rotation),
                    )

                if not object.properties.get("soft", False) and layer == Layer.Objects:
                    self.world.add_component(entity, Solid())

                if id := object.properties.get("item", False):
                    for comp in utils.make.item_comps(id, own_surface=consume_image):
                        self.world.add_component(entity, comp)
            case Layer.Creatures:
                if not (id := object.properties.get("creature", None)):
                    return

                if id not in CREATURES:
                    raise CreatureNotFoundError(
                        f"Существо c идентификатором {id} не найдено в регистре существ."
                    )

                extra_comps = []

                # Использовать картинку, заданную в Tiled, вместо картинки,
                # указанной в регистре существ.
                if image and (
                    object.properties.get("consume_image", DEFAULT_CONSUME_IMAGE)
                ):
                    extra_comps.append(utils.convert.animation_from_surface(image))

                utils.make.creature(
                    self.world,
                    id,
                    position,
                    *extra_comps,
                    *deepcopy(CREATURES[id]),
                    surface_preprocessor=lambda s: pygame.transform.rotate(s, -90),
                )

    def _fill_objects(self, tilemap: pytmx.TiledMap, location: int):
        for group in tilemap.objectgroups:
            for object in group:
                self._fill_object(group, object, location)

    def _make_location(
        self, location: int, location_id: str, camera_size: Tuple[int, int]
    ):
        tilemap = pytmx.load_pygame(utils.fs.ResourcePath.location_tilemap(location_id))

        self._fill_objects(tilemap, location)

        renderer = pyscroll.BufferedRenderer(
            data=pyscroll.TiledMapData(tilemap),
            size=camera_size,
        )

        sprites = pyscroll.PyscrollGroup(map_layer=renderer)

        return Location(tilemap, renderer, sprites)

    def process(self, location=None, settings=None, **_):
        from meta import Id

        for entity, request in self.world.get_component(LocationInitRequest):
            location = self._make_location(entity, request.id, settings["resolution"])
            self.world.add_component(entity, location)
            self.world.add_component(entity, Id(request.id))
            self.world.remove_component(entity, LocationInitRequest)


class SpawnablePositioningProcessor(esper.Processor):
    def process(self, **_):
        from object import ObjectNotFoundError

        location_id, location = utils.get.location(self, id=True)

        for ent, point in self.world.get_component(SpawnPoint):
            if self.world.has_component(ent, Position):
                continue

            for group in location.map.objectgroups:
                for object in group:
                    object: pytmx.TiledObject
                    if object.name == point.name:
                        layer = Layer.from_str(group.name)
                        break
                    object = None
                else:
                    continue
                break

            if not object:
                raise ObjectNotFoundError(f"Объект с именем {point.name} не найден")

            points = object.as_points
            coords = pygame.Vector2(points[0] if len(points) == 1 else points[1])

            self.world.add_component(ent, Position(location_id, coords, layer))
