import pygame
import esper

from creature import PlayerMarker
from location import Layer, Location, Position


class RoofTogglingProcessor(esper.Processor):
    def process(self, **_):
        for _, (_, pos) in self.world.get_components(PlayerMarker, Position):
            location = self.world.component_for_entity(pos.location, Location)
            coords = pos.coords

            tile_width = location.map.tilewidth
            tiles = map(
                lambda t: (
                    t,
                    pygame.Vector2(t[0] * tile_width, t[1] * tile_width),
                    pygame.Vector2(
                        t[0] * tile_width + tile_width - 1,
                        t[1] * tile_width + tile_width - 1,
                    ),
                ),
                location.map.layers[Layer.Roofs].tiles(),
            )

            for tile, start_coords, end_coords in tiles:
                surface = tile[-1]
                if (
                    start_coords.x <= coords.x <= end_coords.x
                    and start_coords.y <= coords.y <= end_coords.y
                ):
                    surface.set_alpha(0)
                else:
                    surface.set_alpha(1000)
