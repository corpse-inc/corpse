import pygame
import esper

from dataclasses import dataclass as component

from location import Position


@component
class Velocity:
    vector: pygame.Vector2


class MovementProcessor(esper.Processor):
    def process(self, dt, screen, running):
        for _, (pos, vel) in self.world.get_components(Position, Velocity):
            vec = vel.vector
            if (vec.x, vec.y) == (0, 0):
                continue
            pos.coords += vec
