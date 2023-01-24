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
        from render import Collision

        if not (ret := utils.get.player(self, Collision, id=True)):
            return

        player, collision = ret

        if self.world.has_component(collision.entity, Item):
            self.world.add_component(player, CollidedItem(collision.entity))


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

                    if gun.ammo > gun.ammo_capacity:
                        gun.ammo = gun.ammo_capacity

                    break


@component
class FireRate:
    # Скорострельность. Задержка между временем выхода пуль из ствола в мс.
    delay: int

    _delay: Optional[int] = None


@component
class Gun:
    # Строковый id предмета патрона.
    ammo_id: str

    # Максимальное коль-во патронов в обойме
    ammo_capacity: int

    # Текущее коль-во патронов в обойме
    ammo: int = 0

    # Отдача оружия. Насколько градусов будет повёрнуто существо при выстрее.
    recoil: int = 10

    # Дальность стрельбы оружия в пикселях.
    range: float = 32 * 20

    _fire_rate: Optional[int] = None


@component
class Ammo:
    # Коль-во патронов в одном предмете
    amount: int


ITEMS = {}


def init_items_registry(world: esper.World):
    from creature import PlayerUninitialized, Damage
    from shoot import FireRate

    if not (player := utils.get.player(world)):
        raise PlayerUninitialized("Игрок не инициализирован")

    registry = {
        "pistol": (
            Gun("pistol_ammo", 8),
            FireRate(400),
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
            Gun("machine_gun_ammo", 5000, recoil=90),
            # FireRate(50),
            About(
                "Миниган",
                "Эта пушка способна уничтожать зомби пачками.",
            ),
        ),
        "machine_gun_ammo": (
            Ammo(5000),
            Damage(100),
            About(
                "Патроны 7.62×51мм",
                f"50 патронов, которыми можно зарядить, например, {ITEM_NAME_FORMATTING.format('Миниган')}",
            ),
        ),
        "sniper_rifle": (
            Gun("sniper_rifle_ammo", 5, recoil=180),
            FireRate(1000),
            About(
                "AWP",
                "Cнайперская винтовка британского производства.",
            ),
        ),
        "sniper_rifle_ammo": (
            Ammo(5),
            Damage(50),
            About(
                "Патроны .300 калибра",
                f"5 патронов, которыми можно зарядить, например, {ITEM_NAME_FORMATTING.format('AWP')}",
            ),
        ),
    }

    for key, val in registry.items():
        ITEMS[key] = val
