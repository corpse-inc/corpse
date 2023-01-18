import pygame
import esper
from meta import About
import utils

from dataclasses import dataclass as component


@component
class ItemsGroup:
    group: pygame.sprite.Group = pygame.sprite.Group()


@component
class Item:
    pass


@component
class CollidedItem:
    entity: int


class ItemNotFoundError(Exception):
    pass


ITEMS = {
    "gun": (About("Оружие"),),
}


class ItemCollisionDetectingProcessor(esper.Processor):
    def process(self, **_):
        from render import Renderable

        player, player_render = utils.get.player(self, Renderable, id=True)

        if not player_render.sprite:
            return

        for item, (_, item_render) in self.world.get_components(Item, Renderable):
            if pygame.sprite.collide_mask(player_render.sprite, item_render.sprite):
                self.world.add_component(player, CollidedItem(item))


class RemoveItemCollidingMarker(esper.Processor):
    def process(self, **_):
        for ent, item in self.world.get_component(CollidedItem):
            self.world.remove_component(ent, CollidedItem)


class ItemsGroupingProcessor(esper.Processor):
    def process(self, **_):
        from render import Renderable

        items_group = utils.get.items_group(self).group
        for _, (render, _) in self.world.get_components(Renderable, Item):
            if render.sprite is not None and render.sprite not in items_group:
                if render._old_sprite:
                    items_group.remove(render._old_sprite)
                items_group.add(render.sprite)
