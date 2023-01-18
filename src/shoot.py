import esper
import pygame
import utils

from dataclasses import dataclass as component


@component
class Shot:
    dir: pygame.Vector2


class ShootingProcessor(esper.Processor):
    def process(self, **_):
        pass
