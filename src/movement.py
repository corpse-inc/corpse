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
        from render import Collision
        from object import Solid, BumpMarker
        from location import Location, Position

        player = utils.get.player(self)

        for moving, (vel, pos) in self.world.get_components(
            Velocity,
            Position,
        ):
            vec = vel.vector
            if (vec.x, vec.y) == (0, 0):
                continue

            location = self.world.component_for_entity(pos.location, Location)
            map_x, map_y = utils.get.location_map_size(location)

            map_bounds = utils.consts.TILEMAP_BOUNDS

            map_x -= map_bounds
            map_y -= map_bounds

            new_coords = pos.coords + vec

            if player and moving == player:
                if new_coords.x >= map_x or new_coords.x <= map_bounds:
                    new_coords.x = pos.coords.x
                if new_coords.y >= map_y or new_coords.y <= map_bounds:
                    new_coords.y = pos.coords.y

            for object, (_, collision) in self.world.get_components(Solid, Collision):
                if moving == object:
                    continue

                if collision.entity == moving:
                    new_coords = pos.coords
                    self.world.add_component(moving, BumpMarker(object))
                    self.world.add_component(object, BumpMarker(moving))

            pos.coords = new_coords


@component
class Direction:
    angle: float


@component
class SetDirectionRequest:
    angle: float


@component
class SetDirectionRequestApprove:
    pass


@component
class LookAfterMouseCursor:
    pass


class DirectionSettingProcessor(esper.Processor):
    def process(self, **_):
        for entity, (_, req) in self.world.get_components(
            SetDirectionRequestApprove, SetDirectionRequest
        ):
            if dir := self.world.try_component(entity, Direction):
                dir.angle = req.angle

            self.world.remove_component(entity, SetDirectionRequestApprove)
            self.world.remove_component(entity, SetDirectionRequest)


class RotationProcessor(esper.Processor):
    """Вращает объекты при необходимости."""

    def process(self, **_):
        from location import Position

        location = utils.get.location(self)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        for entity, (_, pos) in self.world.get_components(
            LookAfterMouseCursor, Position
        ):
            rotation_vector = mouse_pos - pygame.Vector2(
                location.renderer.translate_point(pos.coords)
            )

            self.world.add_component(
                entity, SetDirectionRequest(utils.math.vector_angle(rotation_vector))
            )
