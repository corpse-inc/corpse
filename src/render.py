import pygame
import esper
import utils

from copy import copy
from dataclasses import dataclass as component


@component
class MakeRenderableRequest:
    pass


@component
class MakeUnrenderableRequest:
    pass


@component
class Sprite:
    original_image: pygame.surface.Surface
    sprite: pygame.sprite.Sprite


@component
class SpriteImageChangedMarker:
    pass


class SpriteMakingProcessor(esper.Processor):
    def process(self, **_):
        from object import Size
        from location import Position
        from animation import Animation

        for entity, (_, ani, pos) in self.world.get_components(
            MakeRenderableRequest, Animation, Position
        ):
            if self.world.has_component(entity, Sprite):
                continue

            sprite = utils.make.sprite_component(ani, pos)

            if size := self.world.try_component(entity, Size):
                sprite.original_image = pygame.transform.scale(
                    sprite.original_image, (size.w, size.h)
                )

            self.world.add_component(entity, sprite)
            self.world.add_component(entity, SpriteImageChangedMarker())
            self.world.remove_component(entity, MakeRenderableRequest)


class SpriteAnimationSyncingProcessor(esper.Processor):
    def process(self, **_):
        from animation import Animation

        for entity, (ani, sprite) in self.world.get_components(Animation, Sprite):
            sprite.original_image = utils.convert.surface_from_animation(ani)
            self.world.add_component(entity, SpriteImageChangedMarker)


class SpriteSortingProcessor(esper.Processor):
    def process(self, **_):
        from location import Position

        location = utils.get.location(self)

        for _, (sprite, pos) in self.world.get_components(Sprite, Position):
            if sprite.sprite not in location.sprites:
                location.sprites.add(sprite.sprite, layer=pos.layer.value)


class SpriteRemovingProcessor(esper.Processor):
    def process(self, **_):
        location = utils.get.location(self)

        for entity, _ in self.world.get_component(MakeUnrenderableRequest):
            if not (sprite := self.world.try_component(entity, Sprite)):
                continue

            location.sprites.remove(sprite.sprite)
            self.world.remove_component(entity, Sprite)
            self.world.remove_component(entity, MakeUnrenderableRequest)


class SizeApplyingProcessor(esper.Processor):
    def process(self, **_):
        from object import Size

        for entity, (sprite, size) in self.world.get_components(Sprite, Size):
            if sprite.sprite.image.get_size() == (size.w, size.h):
                continue

            sprite.sprite.image = pygame.transform.scale(
                sprite.original_image, (size.w, size.h)
            )

            self.world.add_component(entity, SpriteImageChangedMarker())


class DirectionApplyingProcessor(esper.Processor):
    def process(self, **_):
        from location import Position
        from object import BumpMarker, Solid
        from movement import Direction, SetDirectionRequest, SetDirectionRequestApprove

        for _, (dir, sprite) in self.world.get_components(Direction, Sprite):
            sprite.sprite.image = pygame.transform.rotate(
                sprite.original_image, -dir.angle
            )

        for entity, (sprite, dir_req) in self.world.get_components(
            Sprite, SetDirectionRequest
        ):
            old_image = sprite.sprite.image.copy()
            old_rect = sprite.sprite.rect.copy()
            old_mask = copy(sprite.sprite.mask)

            sprite.sprite.image = pygame.transform.rotate(
                sprite.original_image, -dir_req.angle
            )
            sprite.sprite.rect = sprite.sprite.image.get_rect()
            sprite.sprite.mask = pygame.mask.from_surface(sprite.sprite.image)

            if pos := self.world.try_component(entity, Position):
                sprite.sprite.rect.center = pos.coords

            for other_entity, (_, other_sprite) in self.world.get_components(
                Solid, Sprite
            ):
                if entity == other_entity:
                    continue

                if pygame.sprite.collide_mask(sprite.sprite, other_sprite.sprite):
                    self.world.add_component(entity, BumpMarker(other_entity))
                    self.world.add_component(other_entity, BumpMarker(entity))

                    sprite.sprite.image = old_image
                    sprite.sprite.rect = old_rect
                    sprite.sprite.mask = old_mask

                    break
            else:
                self.world.add_component(entity, SetDirectionRequestApprove())
                self.world.add_component(entity, SpriteImageChangedMarker())


class SpriteMaskComputingProcessor(esper.Processor):
    def process(self, **_):
        for _, (_, sprite) in self.world.get_components(
            SpriteImageChangedMarker, Sprite
        ):
            sprite.sprite.mask = pygame.mask.from_surface(sprite.sprite.image)


class SpriteRectUpdatingProcessor(esper.Processor):
    def process(self, **_):
        from location import Position

        for _, (sprite, pos) in self.world.get_components(Sprite, Position):
            sprite.sprite.rect = sprite.sprite.image.get_rect(center=pos.coords)


class SpriteImageChangedMarkerRemovingProcessor(esper.Processor):
    def process(self, **_):
        for entity, _ in self.world.get_component(SpriteImageChangedMarker):
            self.world.remove_component(entity, SpriteImageChangedMarker)


class InvisibilityApplyingProcessor(esper.Processor):
    def process(self, **_):
        from object import Invisible

        for _, (_, sprite) in self.world.get_components(Invisible, Sprite):
            sprite.sprite.image.set_alpha(0)


class SpriteDrawingProcessor(esper.Processor):
    def process(self, screen=None, **_):
        utils.get.location(self).sprites.draw(screen)
