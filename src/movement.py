import pygame
import esper
import utils

from typing import Optional
from dataclasses import dataclass as component


@component
class Velocity:
    vector: pygame.Vector2


class MovementProcessor(esper.Processor):
    """Перемещает каждую перемещаемую сущность на заданный вектор скорости."""

    def process(self, **_):
        from location import Location, Position
        from creature import Creature
        from object import Solid
        from render import Renderable

        for _, (_, render) in self.world.get_components(Creature, Renderable):
            creature_sprite = render.sprite

            for _, (pos, vel) in self.world.get_components(Position, Velocity):
                vec = vel.vector
                if (vec.x, vec.y) == (0, 0):
                    continue

                location = self.world.component_for_entity(pos.location, Location)
                map_x, map_y = utils.get.location_map_size(location)

                new_coords = pos.coords + vec

                if new_coords.x >= map_x or new_coords.x <= 0:
                    new_coords.x = pos.coords.x
                if new_coords.y >= map_y or new_coords.y <= 0:
                    new_coords.y = pos.coords.y

                for _, (_, render) in self.world.get_components(Solid, Renderable):
                    object_sprite = render.sprite

                    creature_sprite.rect.center = new_coords

                    if object_sprite is not None and pygame.sprite.collide_mask(
                        creature_sprite, object_sprite
                    ):
                        new_coords = pos.coords

                    creature_sprite.rect.center = pos.coords

                pos.coords = new_coords


@component
class Direction:
    vector: Optional[pygame.Vector2] = None
    angle: Optional[float] = None


class RotationProcessor(esper.Processor):
    """Вращает объекты при необходимости."""

    def _rotate_player(self):
        """Поворачивает игрока так, чтобы он смотрел на курсор мыши."""

        from location import Position

        player, pos = utils.get.player(self, Position, id=True)
        location = utils.get.location(self)

        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(location.renderer.translate_point(pos.coords))

        rotation_vector = mouse_pos - player_pos
        rotation_angle = utils.math.vector_angle(rotation_vector)

        if (dir := self.world.try_component(player, Direction)) is not None:
            dir.vector = rotation_vector
            dir.angle = rotation_angle
        else:
            self.world.add_component(player, Direction(rotation_vector, rotation_angle))

    def process(self, **_):
        self._rotate_player()
