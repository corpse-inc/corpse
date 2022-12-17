from dataclasses import dataclass as component
import pygame


# default component for all item
@component
class Item:
    icon: pygame
    

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
    max: itn

   damage: int


@component
class Ammo:
    id: int
    damage: int


@component
class Armor:
    resistance: float


