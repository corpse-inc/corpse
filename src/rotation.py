import esper
import pygame

from creature import PlayerMarker
from location import Location, Position
from movement import Direction


class RotationProcessor(esper.Processor):
    """Вращает объекты при необходимости."""

    def process(self, **_):
        # Повернуть игрока так, чтобы он смотрел на курсор мыши
        for player, (_, pos) in self.world.get_components(PlayerMarker, Position):
            location = self.world.component_for_entity(pos.location, Location)

            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            player_pos = pygame.Vector2(location.renderer.translate_point(pos.coords))

            rotation_vector = mouse_pos - player_pos

            if (dir := self.world.try_component(player, Direction)) is not None:
                dir.vector = rotation_vector
            else:
                self.world.add_component(player, Direction(rotation_vector))
