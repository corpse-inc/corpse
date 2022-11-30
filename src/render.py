import math
import pygame
import esper
import utils

from dataclasses import dataclass as component

from movement import Direction
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
    координатами и отрисовывает все спрайты на локации, повернув их на нужное
    количество градусов при наличии компонента Direction."""

    def process(self, screen=None, **_):
        for _, (_, position) in self.world.get_components(PlayerMarker, Position):
            location = self.world.component_for_entity(position.location, Location)
            location.sprites.empty()

            for entity, (render, ani, pos) in self.world.get_components(
                Renderable, Animation, Position
            ):
                img = utils.surface_from_animation(ani)
                rect = img.get_rect()
                rect.center = pos.coords

                if (dir := self.world.try_component(entity, Direction)) is not None:
                    angle = dir.vector.as_polar()[1]
                    img = pygame.transform.rotozoom(img, -angle, 1)
                    rect = img.get_rect(center=rect.center)

                sprite = pygame.sprite.Sprite()
                sprite.image = img
                sprite.rect = rect

                if sprite not in location.sprites:
                    location.sprites.add(sprite, layer=pos.layer.value)

                render.sprite = sprite

            if screen is not None:
                location.sprites.draw(screen)

            pygame.display.flip()
