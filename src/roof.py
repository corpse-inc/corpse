import pygame
import esper

import location as loc

import utils

# from location import Layer, Location, Position


class RoofTogglingProcessor(esper.Processor):
    def process(self, **_):
        pos = utils.player(self, loc.Position)
        location = loc.current(self, pos)
        return

        roofs = map(
            lambda object: (object, map(pygame.Vector2, object.as_points)),
            location.map.layers[loc.Layer.Roofs],
        )

        for roof, (p1, p2, p3, p4) in roofs:
            if p1.x <= coords.x <= p4.x and p1.y <= coords.x <= p4.y:
                pass
