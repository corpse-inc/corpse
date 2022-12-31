from dataclasses import dataclass as component
import pygame
import esper
import utils


class SolidGroupingProcessor(esper.Processor):
    def process(self, screen=None, **_):
        from render import Renderable

        solid_group = utils.solid_group(self).group
        for _, (render, _) in self.world.get_components(Renderable, Solid):
            if render.sprite is not None and render.sprite not in solid_group:
                solid_group.add(render.sprite)


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
class Invisible:
    pass
