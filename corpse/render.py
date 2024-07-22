import pygame
import esper
import utils

from typing import List
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


@component
class Collision:
    entities: List[int]


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
            if location.sprites.get_layer_of_sprite(render.sprite) != pos.layer.value:
                location.sprites.change_layer(render.sprite, pos.layer.value)


class SpriteRemovingProcessor(esper.Processor):
    def process(self, **_):
        location = utils.get.location(self)

        for entity, _ in self.world.get_component(MakeUnrenderableRequest):
            if not (render := self.world.try_component(entity, Sprite)):
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
        from movement import Direction, SetDirectionRequest, SetDirectionRequestApprove

        for _, (dir, render) in self.world.get_components(Direction, Sprite):
            render.sprite.image = pygame.transform.rotate(
                render.original_image, -dir.angle
            )

        for entity, (render, _) in self.world.get_components(
            Sprite, SetDirectionRequest
        ):
            self.world.add_component(entity, SetDirectionRequestApprove())
            self.world.add_component(entity, SpriteImageChangedMarker())


class SpriteMaskComputingProcessor(esper.Processor):
    def process(self, **_):
        for _, (_, render) in self.world.get_components(
            SpriteImageChangedMarker, Sprite
        ):
            render.sprite.mask = pygame.mask.from_surface(render.sprite.image)


class CollisionHandlingProcessor(esper.Processor):
    def process(self, **_):
        for entity1, render1 in self.world.get_component(Sprite):
            collides = []
            for entity2, render2 in self.world.get_component(Sprite):
                if entity1 == entity2:
                    continue
                if pygame.sprite.collide_mask(render1.sprite, render2.sprite):
                    collides.append(entity2)
            self.world.add_component(entity1, Collision(collides))


class CollisionRemovingProcessor(esper.Processor):
    def process(self, **_):
        for entity, _ in self.world.get_component(Collision):
            self.world.remove_component(entity, Collision)


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
