import pygame
import esper
import utils

from dataclasses import dataclass as component
from typing import Optional


class SolidGroupingProcessor(esper.Processor):
    def process(self, screen=None, **_):
        from render import Renderable

        solid_group = utils.get.solid_group(self).group
        for _, (render, _) in self.world.get_components(Renderable, Solid):
            if render.sprite is not None and render.sprite not in solid_group:
                solid_group.add(render.sprite)


class BumpMarkerRemovingProcessor(esper.Processor):
    def process(self, **_):
        for ent, _ in self.world.get_component(BumpMarker):
            self.world.remove_component(ent, BumpMarker)


@component
class SolidGroup:
    group: pygame.sprite.Group = pygame.sprite.Group()


@component
class Size:
    w: float
    h: float


@component
class Solid:
    pass


@component
class BumpMarker:
    """Компонент-маркер, обозначающий столкновение твёрдой (Solid) сущности с
    другой твёрдой сущностью (entity)."""

    entity: Optional[int] = None


@component
class Invisible:
    pass


class ObjectNotFoundError(Exception):
    pass
