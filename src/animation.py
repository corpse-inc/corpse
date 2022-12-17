import esper
import pygame

from enum import Enum, auto
from typing import Set, Tuple
from dataclasses import dataclass as component

from movement import Velocity
from object import Invisible


class StateType(Enum):
    Stands = auto()
    Walks = auto()
    HoldsGun = auto()
    HoldsEdgedWeapon = auto()
    Punches = auto()


@component
class States:
    value: Set[StateType]


@component
class Animation:
    frames: Tuple[pygame.surface.Surface]
    delay: int = 0
    paused: bool = False
    children: Tuple[int] = ()
    _frame: int = 0
    _delay: int = 0


class PartType(Enum):
    Legs = auto()


@component
class Part:
    parent: int
    type: PartType


class FrameCyclingProcessor(esper.Processor):
    """Изменяет текущий кадр каждой анимируемой сущности."""
    
    def process(self, dt=None, **_):
        for _, ani in self.world.get_component(Animation):
            if ani.paused:
                continue

            if ani.delay:
                if ani._delay <= 0:
                    ani._delay = ani.delay
                else:
                    ani._delay -= dt
                    continue

            ani._frame += 1
            if ani._frame >= len(ani.frames):
                ani._frame = 0


class StateChangingProcessor(esper.Processor):
    def process(self, **_):
        for _, (states_comp, vel) in self.world.get_components(States, Velocity):
            states = set()

            if vel.vector == pygame.Vector2(0):
                states.add(StateType.Stands)
            else:
                states.add(StateType.Walks)

            states_comp.value.clear()
            states_comp.value.update(states)


class StateHandlingProcessor(esper.Processor):
    def process(self, **_):
        for _, (ani, states) in self.world.get_components(Animation, States):
            states = states.value
            for part_ent in ani.children:
                part = self.world.component_for_entity(part_ent, Part).type
                if part == PartType.Legs and StateType.Stands in states:
                    self.world.add_component(part_ent, Invisible())
                elif self.world.try_component(part_ent, Invisible):
                    self.world.remove_component(part_ent, Invisible)
