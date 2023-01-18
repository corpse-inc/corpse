import pygame
import esper
import utils

from typing import Optional
from dataclasses import dataclass as component


@component
class Renderable:
    sprite: Optional[pygame.sprite.Sprite] = None
    _old_sprite: Optional[pygame.sprite.Sprite] = None


class RenderProcessor(esper.Processor):
    """Добавляет все недобавленные в локацию анимированные сущности с
    координатами и отрисовывает все спрайты на локации, повернув их на нужное
    количество градусов при наличии компонента Direction."""

    def process(self, screen=None, **_):
        from location import Position
        from movement import Direction
        from animation import Animation
        from object import Size, Invisible, BumpMarker

        location = utils.get.location(self)
        location.sprites.empty()

        solid_sprites = utils.get.solid_group(self).group
        item_sprites = utils.get.items_group(self).group

        for entity, (render, ani, pos) in self.world.get_components(
            Renderable, Animation, Position
        ):
            if self.world.try_component(entity, Invisible):
                continue

            img = utils.convert.surface_from_animation(ani)

            if size := self.world.try_component(entity, Size):
                img = pygame.transform.scale(img, (size.w, size.h))

            if (dir := self.world.try_component(entity, Direction)) and dir.angle != 0:
                rotate_img = pygame.transform.rotate(img.convert_alpha(), -dir.angle)

                sprite = utils.make.sprite(
                    rotate_img,
                    rotate_img.get_rect(center=pos.coords),
                    pygame.mask.from_surface(rotate_img),
                )

                solid_sprites.remove(render._old_sprite)
                if not pygame.sprite.spritecollideany(
                    sprite, solid_sprites, collided=pygame.sprite.collide_mask
                ):
                    img = rotate_img
                elif render._old_sprite is not None:
                    self.world.add_component(entity, BumpMarker())
                    img = render._old_sprite.image

            sprite = utils.make.sprite(
                img,
                img.get_rect(center=pos.coords),
                pygame.mask.from_surface(img),
            )

            if sprite not in location.sprites:
                location.sprites.add(sprite, layer=pos.layer.value)

            render.sprite = sprite
            render._old_sprite = sprite

        solid_sprites.empty()
        item_sprites.empty()

        if screen is not None:
            location.sprites.draw(screen)
