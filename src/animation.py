import esper
import pygame

from enum import Enum, auto
from dataclasses import dataclass as component


class AnimationState(Enum):
    Stands = auto()
    Runs = auto()
    HoldsGun = auto()
    HoldsEdgedWeapon = auto()
    Punches = auto()


@component
class Animation:
    state: tuple[AnimationState]
    frames: dict[tuple[AnimationState], tuple[pygame.surface.Surface]]
    frame_idx: int = 0


class FrameCyclingProcessor(esper.Processor):
    """Изменяет текущий кадр каждой анимируемой сущности."""

    def process(self, **_):
        for _, ani in self.world.get_component(Animation):
            ani.frame_idx += 1
            if ani.frame_idx >= len(ani.frames[ani.state]):
                ani.frame_idx = 0
