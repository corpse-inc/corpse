import pygame
import esper
import utils

from dataclasses import dataclass as component
from animation import Animation

from creature import Creature, PlayerMarker
from location import Location, Position


class Sprite(pygame.sprite.Sprite):
    def __init__(self, surface):
        self.image = surface
        self.rect = surface.get_rect()


@component
class Renderable:
    sprite: Sprite | None = None


class RenderProcessor(esper.Processor):
    def process(self, dt, screen, running):
        for _, (_, position) in self.world.get_components(PlayerMarker, Position):
            location = self.world.component_for_entity(position.location, Location)

            for _, (render, ani) in self.world.get_components(Renderable, Animation):
                sprite = pygame.sprite.Sprite()
                sprite.image = utils.surface_from_animation(ani)
                sprite.rect = sprite.image.get_rect()
                if sprite not in location.sprites:
                    location.sprites.add(sprite)

            location.sprites.draw(screen)
            pygame.display.flip()
