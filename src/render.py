import pygame
import esper
from pygame.sprite import collide_mask
import utils

from dataclasses import dataclass as component


@component
class Renderable:
    sprite: pygame.sprite.Sprite | None = None
    _old_sprite: pygame.sprite.Sprite | None = None


class RenderProcessor(esper.Processor):
    """Добавляет все недобавленные в локацию анимированные сущности с
    координатами и отрисовывает все спрайты на локации, повернув их на нужное
    количество градусов при наличии компонента Direction."""

    def process(self, screen=None, **_):
        from location import Position
        from animation import Animation
        from movement import Direction
        from object import Size, Invisible

        location = utils.location(self)
        location.sprites.empty()

        solid_sprites = utils.solid_group(self).group

        for entity, (render, ani, pos) in self.world.get_components(
            Renderable, Animation, Position
        ):
            if self.world.try_component(entity, Invisible):
                continue

            img = utils.surface_from_animation(ani)

            if (size := self.world.try_component(entity, Size)) is not None:
                img = pygame.transform.scale(img, (size.w, size.h))

            if (
                dir := self.world.try_component(entity, Direction)
            ) is not None and dir.angle != 0:
                if dir.angle is None:
                    dir.angle = utils.vector_angle(dir.vector)

                rotate_img = pygame.transform.rotate(img.convert_alpha(), -dir.angle)

                sprite = utils.sprite(
                    rotate_img,
                    rotate_img.get_rect(center=pos.coords),
                    pygame.mask.from_surface(rotate_img),
                )

                if not pygame.sprite.spritecollideany(
                    sprite, solid_sprites, collided=pygame.sprite.collide_mask
                ):
                    img = rotate_img
                elif render._old_sprite is not None:
                    img = render._old_sprite.image

            sprite = utils.sprite(
                img,
                img.get_rect(center=pos.coords),
                pygame.mask.from_surface(img),
            )

            if sprite not in location.sprites:
                location.sprites.add(sprite, layer=pos.layer.value)

            render.sprite = sprite
            render._old_sprite = sprite

        solid_sprites.empty()

        if screen is not None:
            location.sprites.draw(screen)
