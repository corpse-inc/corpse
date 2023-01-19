import pygame
import esper
import utils

from typing import Optional, Sequence
from copy import deepcopy
from dataclasses import dataclass as component

from meta import About


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
        from render import Sprite

        player, player_render = utils.get.player(self, Sprite, id=True)

        if not player_render.sprite:
            return

        for item, (_, item_render) in self.world.get_components(Item, Sprite):
            if pygame.sprite.collide_mask(player_render.sprite, item_render.sprite):
                self.world.add_component(player, CollidedItem(item))


class RemoveItemCollidingMarker(esper.Processor):
    def process(self, **_):
        for ent, _ in self.world.get_component(CollidedItem):
            self.world.remove_component(ent, CollidedItem)


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
        from render import MakeUnrenderableRequest

        for ent, (inv, take) in self.world.get_components(Inventory, TakeItemRequest):
            for i in range(len(inv.slots)):
                if inv.slots[i] is None:
                    inv.slots[i] = take.entity

                    if self.world.has_component(take.entity, Position):
                        self.world.remove_component(take.entity, Position)

                    self.world.add_component(take.entity, MakeUnrenderableRequest())

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
        from location import Layer
        from location import Position
        from render import MakeRenderableRequest

        for ent, (ground, inv, pos) in self.world.get_components(
            GroundItem, Inventory, Position
        ):
            item = inv.slots.pop(ground.item)

            self.world.add_component(
                item, Position(pos.location, deepcopy(pos.coords), Layer.Items)
            )
            self.world.add_component(item, MakeRenderableRequest())
            self.world.remove_component(ent, GroundItem)
