import pygame
import esper

from creature import PlayerMarker
from location import Layer, Location, Position


class RoofTogglingProcessor(esper.Processor):
    def process(self, **_):
        for _, (_, pos) in self.world.get_components(PlayerMarker, Position):
            location = self.world.component_for_entity(pos.location, Location)
            coords = pos.coords

            roofs = map(
                lambda object: (object, map(pygame.Vector2, object.as_points)),
                location.map.layers[Layer.Roofs],
            )

            for roof, (p1, p2, p3, p4) in roofs:
                if p1.x <= coords.x <= p4.x and p1.y <= coords.x <= p4.y:
                    pass
