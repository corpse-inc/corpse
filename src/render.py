import pygame
import esper
import utils

from dataclasses import dataclass as component

import movement as mov

from animation import Animation

import location as loc


@component
class Renderable:
    sprite: pygame.sprite.Sprite | None = None


class RenderProcessor(esper.Processor):
    """Добавляет все недобавленные в локацию анимированные сущности с
    координатами и отрисовывает все спрайты на локации, повернув их на нужное
    количество градусов при наличии компонента Direction."""

    def process(self, screen=None, **_):
        location = loc.current(self)
        location.sprites.empty()

        for entity, (render, ani, pos) in self.world.get_components(
            Renderable, Animation, loc.Position
        ):
            img = utils.surface_from_animation(ani)
            rect = img.get_rect(center=pos.coords)

            if render.sprite is not None:
                pass

            if (dir := self.world.try_component(entity, mov.Direction)) is not None:
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
