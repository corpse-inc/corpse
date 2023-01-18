from copy import deepcopy
import pygame
import esper
import utils

from typing import Optional, Sequence
from dataclasses import dataclass as component

from meta import About


@component
class ItemsGroup:
    group: pygame.sprite.Group = pygame.sprite.Group()


@component
class Item:
    pass


@component
class CollidedItem:
    entity: int


@component
class TakeItemRequest:
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
        for ent, _ in self.world.get_component(CollidedItem):
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


@component
class Inventory:
    capacity: int
    slots: Optional[Sequence[Optional[int]]] = None


class InventoryInitializingProcessor(esper.Processor):
    def process(self, **_):
        for _, inv in self.world.get_component(Inventory):
            if inv.slots is None:
                inv.slots = []

            while len(inv.slots) < inv.capacity:
                inv.slots.append(None)


class InventoryFillingProcessor(esper.Processor):
    def process(self, **_):
        for _, inv in self.world.get_component(Inventory):
            while len(inv.slots) < inv.capacity:
                inv.slots.append(None)


class ItemsTakingProcessor(esper.Processor):
    def process(self, **_):
        from location import Position
        from render import Renderable

        for ent, (inv, take) in self.world.get_components(Inventory, TakeItemRequest):
            for i in range(len(inv.slots)):
                if inv.slots[i] is None:
                    inv.slots[i] = take.entity
                    remove_comps = (Position, Renderable)

                    for comp in remove_comps:
                        if self.world.has_component(take.entity, comp):
                            self.world.remove_component(take.entity, comp)

                    break

            self.world.remove_component(ent, TakeItemRequest)


@component
class Equipment:
    # индекс экупированного слота в инвентаре
    item: int = 0


@component
class GroundItem:
    item: int


class ItemGroundingProcessor(esper.Processor):
    def process(self, **_):
        from location import Position
        from render import Renderable
        from location import Layer

        for ent, (ground, inv, pos) in self.world.get_components(
            GroundItem, Inventory, Position
        ):
            item = inv.slots.pop(ground.item)

            self.world.add_component(
                item, Position(pos.location, deepcopy(pos.coords), Layer.Items)
            )
            self.world.add_component(item, Renderable())
            self.world.remove_component(ent, GroundItem)
