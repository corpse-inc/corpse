import pygame
import esper

from dataclasses import dataclass as component


@component
class UiElement:
    surface: pygame.surface.Surface
    position: pygame.math.Vector2


class UiDrawingProcessor(esper.Processor):
    def process(self, screen=None, **_):
        for _, elem in self.world.get_component(UiElement):
            screen.blit(elem.surface, elem.position)
