from dataclasses import dataclass as component
import pygame
import esper
import utils

class ItemsProcessor(esper.Processor):
    def process(self, **_):

        from location import Position

        player, pos = utils.player(self, Position, id=True)
        x_player = pos.coords.x
        y_player = pos.coords.y

        items_sprite = utils.items_group(self).group
        for sprite in items_sprite:
            x_item = sprite.rect.x
            y_item = sprite.rect.y
            if (x_player - x_item == 8 or x_item - x_player == 8) and\
                    (y_player - y_item == 8 or y_item - y_player -- 8):
                print("item near")


class ItemsGroupingProcessor(esper.Processor):
    def process(self, screen=None, **_):
        from render import Renderable

        items_group = utils.items_group(self).group
        for _, (render, _) in self.world.get_components(Renderable, Item):
            if render.sprite is not None and render.sprite not in items_group:
                items_group.add(render.sprite)


@component
class ItemsGroup:
    group: pygame.sprite.Group = pygame.sprite.Group()


# default component for all item
@component
class Item:
    pass
    

@component
class About:
    name: str
    description: str


@component
class Position:
    location: int
    coords: pygame.math.Vector2


@component
class Durability:
    times: int


# component for consumables
@component
class ConsumptionComment:
    comments: tuple[str]


@component
class HealRequest:
    creature: int
    amount: int


@component
class SaturateRequest:
    creature: int
    amount: int


@component
class DamageRequest:
    creature: int
    amount: int


# component for weapon
@component
class FireWeapon:
    power: float
    range: int


@component
class EdgedWeapon:
    range: int
 

@component
class Magazine:
    ammo: int
    current: int
    max: int
    damage: int


@component
class Ammo:
    id: int
    damage: int


@component
class Armor:
    resistance: float


