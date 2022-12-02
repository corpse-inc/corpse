import pygame
import esper

from dataclasses import dataclass as component

from location import Position


@component
class Direction:
    vector: pygame.Vector2


@component
class Velocity:
    vector: pygame.Vector2


class MovementProcessor(esper.Processor):
    """Перемещает каждую перемещаемую сущность на заданный вектор скорости."""

    def process(self, **_):
        for _, (pos, vel) in self.world.get_components(Position, Velocity):
            vec = vel.vector
            if (vec.x, vec.y) == (0, 0):
                continue
            
            new_coords = pos + vec
            if new_coords.x >= screen_x or new_coords.x <= 0:
                new_coords.x = pos.coords.x
            if new_coords.y >= screen_y or new_coords.y <= 0:
                new_coords.y = pos.coords.y

            pos.coords = new_coords
