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

            render = utils.make.sprite_component(ani, pos)

            if size := self.world.try_component(entity, Size):
                render.original_image = pygame.transform.scale(
                    render.original_image, (size.w, size.h)
                )

            self.world.add_component(entity, render)
            self.world.add_component(entity, SpriteImageChangedMarker())
            self.world.remove_component(entity, MakeRenderableRequest)


class SpriteAnimationSyncingProcessor(esper.Processor):
    def process(self, **_):
        from animation import Animation

        for entity, (ani, render) in self.world.get_components(Animation, Sprite):
            render.original_image = utils.convert.surface_from_animation(ani)
            self.world.add_component(entity, SpriteImageChangedMarker)


class SpriteSortingProcessor(esper.Processor):
    def process(self, **_):
        from location import Position

        location = utils.get.location(self)

        for _, (render, pos) in self.world.get_components(Sprite, Position):
            if render.sprite not in location.sprites:
                location.sprites.add(render.sprite, layer=pos.layer.value)


class SpriteRemovingProcessor(esper.Processor):
    def process(self, **_):
        location = utils.get.location(self)

        for entity, _ in self.world.get_component(MakeUnrenderableRequest):
            if not (sprite := self.world.try_component(entity, Sprite)):
                continue

            location.sprites.remove(render.sprite)
            self.world.remove_component(entity, Sprite)
            self.world.remove_component(entity, MakeUnrenderableRequest)


class SizeApplyingProcessor(esper.Processor):
    def process(self, **_):
        from object import Size

        for entity, (render, size) in self.world.get_components(Sprite, Size):
            if render.sprite.image.get_size() == (size.w, size.h):
                continue

            render.sprite.image = pygame.transform.scale(
                render.original_image, (size.w, size.h)
            )

            self.world.add_component(entity, SpriteImageChangedMarker())


class DirectionApplyingProcessor(esper.Processor):
    def process(self, **_):
        from location import Position
        from object import BumpMarker, Solid
        from movement import Direction, SetDirectionRequest, SetDirectionRequestApprove

        for _, (dir, render) in self.world.get_components(Direction, Sprite):
            render.sprite.image = pygame.transform.rotate(
                render.original_image, -dir.angle
            )

        for entity, (render, dir_req) in self.world.get_components(
            Sprite, SetDirectionRequest
        ):
            old_image = render.sprite.image.copy()
            old_rect = render.sprite.rect.copy()
            old_mask = copy(render.sprite.mask)

            render.sprite.image = pygame.transform.rotate(
                render.original_image, -dir_req.angle
            )
            render.sprite.rect = render.sprite.image.get_rect()
            render.sprite.mask = pygame.mask.from_surface(render.sprite.image)

            if pos := self.world.try_component(entity, Position):
                render.sprite.rect.center = pos.coords

            for other_entity, (_, other_render) in self.world.get_components(
                Solid, Sprite
            ):
                if entity == other_entity:
                    continue

                if pygame.sprite.collide_mask(render.sprite, other_render.sprite):
                    self.world.add_component(entity, BumpMarker(other_entity))
                    self.world.add_component(other_entity, BumpMarker(entity))

                    render.sprite.image = old_image
                    render.sprite.rect = old_rect
                    render.sprite.mask = old_mask

                    break
            else:
                self.world.add_component(entity, SetDirectionRequestApprove())
                self.world.add_component(entity, SpriteImageChangedMarker())


class SpriteMaskComputingProcessor(esper.Processor):
    def process(self, **_):
        for _, (_, render) in self.world.get_components(
            SpriteImageChangedMarker, Sprite
        ):
            render.sprite.mask = pygame.mask.from_surface(render.sprite.image)


class SpriteRectUpdatingProcessor(esper.Processor):
    def process(self, **_):
        from location import Position

        for _, (render, pos) in self.world.get_components(Sprite, Position):
            render.sprite.rect = render.sprite.image.get_rect(center=pos.coords)


class SpriteImageChangedMarkerRemovingProcessor(esper.Processor):
    def process(self, **_):
        for entity, _ in self.world.get_component(SpriteImageChangedMarker):
            self.world.remove_component(entity, SpriteImageChangedMarker)


class InvisibilityApplyingProcessor(esper.Processor):
    def process(self, **_):
        from object import Invisible

        for _, (_, render) in self.world.get_components(Invisible, Sprite):
            render.sprite.image.set_alpha(0)


class SpriteDrawingProcessor(esper.Processor):
    def process(self, screen=None, settings=None, **_):
        utils.get.location(self).sprites.draw(screen)
        utils.get.location(self).renderer.zoom = settings["zoom"]
