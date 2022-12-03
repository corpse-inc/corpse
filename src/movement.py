import pygame
import esper

from dataclasses import dataclass as component

from creature import PlayerMarker

import utils
import location as loc


@component
class Velocity:
    vector: pygame.Vector2


class MovementProcessor(esper.Processor):
    """Перемещает каждую перемещаемую сущность на заданный вектор скорости."""

    def process(self, **_):
        for _, (pos, vel) in self.world.get_components(loc.Position, Velocity):
            vec = vel.vector
            if (vec.x, vec.y) == (0, 0):
                continue

            location = self.world.component_for_entity(pos.location, loc.Location)
            map_x, map_y = utils.location_map_size(location)

            new_coords = pos.coords + vec
            if new_coords.x >= map_x or new_coords.x <= 0:
                new_coords.x = pos.coords.x
            if new_coords.y >= map_y or new_coords.y <= 0:
                new_coords.y = pos.coords.y

            pos.coords = new_coords


@component
class Direction:
    vector: pygame.Vector2


class RotationProcessor(esper.Processor):
    """Вращает объекты при необходимости."""

    def process(self, **_):
        # Повернуть игрока так, чтобы он смотрел на курсор мыши
        for player, (_, pos) in self.world.get_components(PlayerMarker, loc.Position):
            location = self.world.component_for_entity(pos.location, loc.Location)

            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            player_pos = pygame.Vector2(location.renderer.translate_point(pos.coords))

            rotation_vector = mouse_pos - player_pos

            if (dir := self.world.try_component(player, Direction)) is not None:
                dir.vector = rotation_vector
            else:
                self.world.add_component(player, Direction(rotation_vector))
