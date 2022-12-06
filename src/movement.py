import pygame
import esper

from dataclasses import dataclass as component

from pygame.transform import laplacian
from object import Solid

import utils


@component
class Velocity:
    vector: pygame.Vector2


class MovementProcessor(esper.Processor):
    """Перемещает каждую перемещаемую сущность на заданный вектор скорости."""

    def process(self, **_):
        from location import Location, Position, Layer

        for _, (pos, vel) in self.world.get_components(Position, Velocity):
            vec = vel.vector
            if (vec.x, vec.y) == (0, 0):
                continue

            location = self.world.component_for_entity(pos.location, Location)
            map_x, map_y = utils.location_map_size(location)

            new_coords = pos.coords + vec
            if new_coords.x >= map_x or new_coords.x <= 0:
                new_coords.x = pos.coords.x
            if new_coords.y >= map_y or new_coords.y <= 0:
                new_coords.y = pos.coords.y

            for _, (_, obj_pos) in self.world.get_components(Solid, Position):
                if obj_pos.coords[0] < new_coords.x <= obj_pos.coords[0]:
                    new_coords.x = pos.coords.x 

            pos.coords = new_coords


@component
class Direction:
    vector: pygame.Vector2 | None = None
    angle: float | None = None


class RotationProcessor(esper.Processor):
    """Вращает объекты при необходимости."""

    def _rotate_player(self):
        """Поворачивает игрока так, чтобы он смотрел на курсор мыши."""

        from location import Position

        player, pos = utils.player(self, Position, id=True)
        location = utils.location(self, pos)

        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(location.renderer.translate_point(pos.coords))

        rotation_vector = mouse_pos - player_pos
        rotation_angle = utils.vector_angle(rotation_vector)

        if (dir := self.world.try_component(player, Direction)) is not None:
            dir.vector = rotation_vector
            dir.angle = rotation_angle
        else:
            self.world.add_component(player, Direction(rotation_vector, rotation_angle))

    def process(self, **_):
        self._rotate_player()
