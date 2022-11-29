import pygame
import esper
import utils

from dataclasses import dataclass as component
from animation import Animation

from creature import PlayerMarker
from location import Layer, Location, Position


class Sprite(pygame.sprite.Sprite):
    def __init__(self, surface):
        self.image = surface
        self.rect = surface.get_rect()


@component
class Renderable:
    sprite: Sprite | None = None


class RenderProcessor(esper.Processor):
    """Добавляет все недобавленные в локацию анимированные сущности с
    координатами и отрисовывает все спрайты на локации."""

    def process(self, dt, screen, running):
        for _, (_, position) in self.world.get_components(PlayerMarker, Position):
            location = self.world.component_for_entity(position.location, Location)
            location.sprites.empty()

            for _, (render, ani, pos) in self.world.get_components(
                Renderable, Animation, Position
            ):
                sprite = pygame.sprite.Sprite()
                sprite.image = utils.surface_from_animation(ani)
                sprite.rect = sprite.image.get_rect()
                sprite.rect.move_ip(*pos.coords)

                if sprite not in location.sprites:
                    location.sprites.add(sprite, layer=pos.layer.value)

                render.sprite = sprite

            location.sprites.draw(screen)
            pygame.display.flip()
