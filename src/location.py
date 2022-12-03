import pygame
import esper
import pytmx
import pyscroll
import utils

from dataclasses import dataclass as component

import render

from creature import PlayerMarker

from position import *


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

        for object in tilemap.objects:
            object: pytmx.TiledObject

            points = object.as_points
            point = (
                sum(map(lambda p: p.x, points)) / len(points),
                sum(map(lambda p: p.y, points)) / len(points),
            )

            entity = self.world.create_entity(
                Position(location, location_id, pygame.Vector2(point)),
            )

            if object.image is not None:
                image = pygame.transform.rotate(object.image, -object.rotation)
                rect = image.get_rect()
                rect.width = object.width
                rect.height = object.height
                self.world.add_component(entity, utils.animation_from_surface(image))
                self.world.add_component(
                    entity, render.Renderable(sprite=utils.sprite(image, rect))
                )

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


def current(processor, player_position: Position | None = None) -> Location:
    world: esper.World = processor.world

    if player_position is not None:
        return world.component_for_entity(player_position.location, Location)

    return world.component_for_entity(
        utils.player(processor, Position).location, Location
    )
