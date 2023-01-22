import pygame
import esper
import utils

from copy import deepcopy
from typing import Optional, Sequence
from dataclasses import dataclass as component

from meta import About, Id
from utils.consts import ITEM_NAME_FORMATTING


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


class ItemCollisionDetectingProcessor(esper.Processor):
    def process(self, **_):
        from render import Sprite

        try:
            player, player_render = utils.get.player(self, Sprite, id=True)
        except TypeError:
            return

        if not (player and player_render):
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
            item = inv.slots[ground.item]
            inv.slots[ground.item] = None

            self.world.add_component(
                item, Position(pos.location, deepcopy(pos.coords), Layer.Items)
            )
            self.world.add_component(item, MakeRenderableRequest())
            self.world.remove_component(ent, GroundItem)


@component
class ReloadGunRequest:
    pass


class GunReloadingProcessor(esper.Processor):
    def process(self, **_):
        for entity, (_, inv, equip) in self.world.get_components(
            ReloadGunRequest, Inventory, Equipment
        ):
            self.world.remove_component(entity, ReloadGunRequest)

            if not (
                inv.slots
                and (current_item := inv.slots[equip.item])
                and (gun := self.world.try_component(current_item, Gun))
            ):
                continue

            for i, item in enumerate(inv.slots):
                if not item:
                    continue

                id = self.world.component_for_entity(item, Id).id

                if id == gun.ammo_id:

                    ammo = self.world.component_for_entity(item, Ammo)

                    if gun.ammo != gun.ammo_capacity:
                        inv.slots[i] = None
                        gun.ammo += ammo.amount
                        break

                    if gun.ammo > gun.ammo_capacity:
                        gun.ammo = gun.ammo_capacity

                    break


@component
class Gun:
    ammo_id: str
    ammo_capacity: int
    ammo: int = 0


@component
class Ammo:
    amount: int


ITEMS = {}


def init_items_registry(world: esper.World):
    from creature import PlayerUninitialized, Damage

    if not (player := utils.get.player(world)):
        raise PlayerUninitialized("Игрок не инициализирован")

    registry = {
        "pistol": (
            Gun("pistol_ammo", 8),
            About(
                "Armscor",
                "Старенький пистолет филиппинского производства.<br>Старый, но надёжный!",
            ),
        ),
        "pistol_ammo": (
            Ammo(8),
            Damage(15),
            About(
                "Патроны .45 калибра",
                f"8 патронов, которыми можно зарядить, например, {ITEM_NAME_FORMATTING.format('Armscor')}",
            ),
        ),
        "machine_gun": (
            Gun("machine_gun_ammo", 50),
            About(
                "Миниган",
                "Эта пушка способна уничтожать зомби пачками.",
            ),
        ),
        "machine_gun_ammo": (
            Ammo(50),
            Damage(15),
            About(
                "Патроны 7.62×51мм",
                f"50 патронов, которыми можно зарядить, например, {ITEM_NAME_FORMATTING.format('Миниган')}",
            ),
        ),
        "sniper_rifle": (
            Gun("sniper_rifle_ammo", 5),
            About(
                "AWP",
                "Cнайперская винтовка британского производства.",
            ),
        ),
        "sniper_rifle_ammo": (
            Ammo(5),
            Damage(15),
            About(
                "Патроны .300 калибра",
                f"5 патронов, которыми можно зарядить, например, {ITEM_NAME_FORMATTING.format('AWP')}",
            ),
        ),
    }

    for key, val in registry.items():
        ITEMS[key] = val
