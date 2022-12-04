import math
import pygame
import esper

import utils

from location import Layer, Position
from object import Invisible, Size


class RoofTogglingProcessor(esper.Processor):
    def process(self, **_):
        px, py = utils.player(self, Position).coords

        for roof, (pos, size) in self.world.get_components(Position, Size):
            if pos.layer != Layer.Roofs:
                continue

            x1, y1 = pos.coords
            x2, y2 = x1 + size.w, y1 + size.h

            if x1 <= px <= x2 and y1 <= py <= y2:
                self.world.add_component(roof, Invisible())
            elif self.world.try_component(roof, Invisible) is not None:
                self.world.remove_component(roof, Invisible)
