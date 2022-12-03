import pygame
import esper

import utils

from location import Position


class RoofTogglingProcessor(esper.Processor):
    def process(self, **_):
        return
        pos = utils.player(self, Position)
        location = utils.location(self, pos)

        roofs = map(
            lambda object: (object, map(pygame.Vector2, object.as_points)),
            location.map.layers[loc.Layer.Roofs],
        )

        for roof, (p1, p2, p3, p4) in roofs:
            if p1.x <= coords.x <= p4.x and p1.y <= coords.x <= p4.y:
                pass
