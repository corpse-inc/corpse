import pygame
import pyscroll
import pytmx

from enum import IntEnum, auto
from dataclasses import dataclass as component


class Layer(IntEnum):
    """Каждая локация имеет три слоя: земля, объекты и крыши. На земле
    расположены тайлы травы, дорог и т. п. На слое объектов расположены все
    существа, объекты и предметы. На слое с крышами расположены крыши строений."""

    # Порядок имеет значение!
    Ground = auto()
    Objects = auto()
    Creatures = auto()
    Roofs = auto()


@component
class Location:
    map: pytmx.TiledMap | None = None
    sprites: pyscroll.PyscrollGroup | None = None
    renderer: pyscroll.BufferedRenderer | None = None


@component
class Position:
    location: int
    location_id: str
    coords: pygame.Vector2
    layer: Layer = Layer.Objects
