import pygame
import esper
from movement import Direction

import utils

from location import Layer, Position
from object import Invisible, Size


class RoofTogglingProcessor(esper.Processor):
    def process(self, **_):
        px, py = utils.player(self, Position).coords

        for roof, (pos, size) in self.world.get_components(Position, Size):
            if pos.layer != Layer.Roofs:
                continue

            hide = False

            origin = pos.coords
            rx1, ry1 = origin - pygame.Vector2(size.w, size.h) / 2
            rx2, ry2 = rx1 + size.w, ry1 + size.h

            if (dir := self.world.try_component(roof, Direction)) is not None:
                x01, y01 = utils.rotate_point(origin, (rx1, ry1), dir.angle)
                x02, y02 = utils.rotate_point(origin, (rx2, ry2), dir.angle)
                x1, y1 = utils.rotate_point(origin, (rx1, ry2), dir.angle)
                x2, y2 = utils.rotate_point(origin, (rx2, ry1), dir.angle)

                if (x01 <= px <= x02 and y01 <= py <= y02) or (
                    x1 <= px <= x2 and y2 <= py <= y1
                ):
                    hide = True

            elif rx1 <= px <= rx2 and ry1 <= py <= ry2:
                hide = True

            if hide:
                self.world.add_component(roof, Invisible())
            elif self.world.try_component(roof, Invisible):
                self.world.remove_component(roof, Invisible)
