import pygame
import esper
import pytmx
import pyscroll
import utils

from dataclasses import dataclass as component

from creature import PlayerMarker


@component
class Location:
    sprites: pyscroll.PyscrollGroup | None = None


@component
class Position:
    location: int
    location_id: str
    coords: pygame.math.Vector2


@component
class SkipLocationInitMarker:
    pass


class InitLocationProcessor(esper.Processor):
    def _make_scroll_group(self, location_id: str):
        tmx_data = pytmx.load_pygame(utils.ResourcePath.location_tilemap(location_id))

        map_layer = pyscroll.BufferedRenderer(
            data=pyscroll.TiledMapData(tmx_data),
            size=utils.RESOLUTION,
        )

        return pyscroll.PyscrollGroup(map_layer=map_layer)

    def process(self, dt, screen, running):
        if len(self.world.get_component(SkipLocationInitMarker)) != 0:
            return

        for _, (_, position) in self.world.get_components(PlayerMarker, Position):
            location = self.world.component_for_entity(position.location, Location)
            location.sprites = self._make_scroll_group(position.location_id)
            self.world.create_entity(SkipLocationInitMarker)
