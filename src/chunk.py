import esper
import pygame
import utils

from creature import PlayerMarker
from location import Position
from typing import Tuple


class ChunkUnloadingProcessor(esper.Processor):
    def process(self, screen_size: Tuple[int, int], world: esper.World):
        w, h = screen_size
        px, py = utils.get.player_from_world(world, Position).coords

        for obj, pos in world.get_component(Position):
            if world.try_component(obj, PlayerMarker):
                continue

            x, y = pos.coords
            b1, b2 = pygame.Vector2(px - w, py - h), pygame.Vector2(px + w, py + h)

            if not (b1.x <= x <= b2.x and b1.y <= y <= b2.y):
                self.world.create_entity(*world.components_for_entity(obj))
                world.delete_entity(obj)


class ChunkLoadingProcessor(esper.Processor):
    def process(self, screen_size: Tuple[int, int], world: esper.World):
        w, h = screen_size
        px, py = utils.get.player_from_world(world, Position).coords

        for obj, pos in self.world.get_component(Position):
            x, y = pos.coords
            b1, b2 = pygame.Vector2(px - w, py - h), pygame.Vector2(px + w, py + h)
            if b1.x <= x <= b2.x and b1.y <= y <= b2.y:
                world.create_entity(*self.world.components_for_entity(obj))
                self.world.delete_entity(obj)
