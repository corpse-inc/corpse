import esper
import utils
import pygame

from dataclasses import dataclass as component


@component
class Velocity:
    vector: pygame.Vector2
    value: float = utils.consts.DEFAULT_SPEED


class MovementProcessor(esper.Processor):
    """Перемещает каждую перемещаемую сущность на заданный вектор скорости."""

    def process(self, **_):
        from render import Renderable
        from object import Solid, BumpMarker
        from location import Location, Position

        for moving, (vel, pos, render) in self.world.get_components(
            Velocity,
            Position,
            Renderable,
        ):
            if not (moving_sprite := render.sprite):
                continue

            vec = vel.vector
            if (vec.x, vec.y) == (0, 0):
                continue

            location = self.world.component_for_entity(pos.location, Location)
            map_x, map_y = utils.get.location_map_size(location)

            map_bounds = 32

            map_x -= map_bounds
            map_y -= map_bounds

            new_coords = pos.coords + vec

            if moving == utils.get.player(self, id=True):
                if new_coords.x >= map_x or new_coords.x <= map_bounds:
                    new_coords.x = pos.coords.x
                if new_coords.y >= map_y or new_coords.y <= map_bounds:
                    new_coords.y = pos.coords.y

            for object, (_, render) in self.world.get_components(Solid, Renderable):
                if moving == object or not (object_sprite := render.sprite):
                    continue

                moving_sprite.rect.center = new_coords

                if object_sprite is not None and pygame.sprite.collide_mask(
                    moving_sprite, object_sprite
                ):
                    new_coords = pos.coords
                    self.world.add_component(moving, BumpMarker(object))

                moving_sprite.rect.center = pos.coords

            pos.coords = new_coords


@component
class Direction:
    vector: pygame.Vector2 = pygame.Vector2(0)
    angle: float = 0


class DirectionAngleCalculationProcessor(esper.Processor):
    def process(self, **_):
        for _, dir in self.world.get_component(Direction):
            if dir.vector:
                dir.angle = utils.math.vector_angle(dir.vector)


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

        if (dir := self.world.try_component(player, Direction)) is not None:
            dir.vector = rotation_vector
        else:
            self.world.add_component(player, Direction(rotation_vector))

    def process(self, **_):
        self._rotate_player()
