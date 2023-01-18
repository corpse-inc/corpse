import utils
import esper
import pygame

from enum import Enum, auto
from typing import Dict, Optional, Set, Tuple
from dataclasses import dataclass as component

from meta import Id
from creature import Health
from object import Invisible
from movement import Velocity


class StateType(Enum):
    Dead = auto()
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
    state_based_frames: Optional[Dict[StateType, Tuple[pygame.surface.Surface]]] = None
    _frame: int = 0
    _delay: int = 0


class PartType(Enum):
    Legs = auto()

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, s: str):
        return cls[utils.convert.snake_to_camel_case(s)]


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
        for entity, states_comp in self.world.get_component(States):
            states = set()

            if vel := self.world.try_component(entity, Velocity):
                if vel.vector == pygame.Vector2(0):
                    states.add(StateType.Stands)
                else:
                    states.add(StateType.Walks)

            if health := self.world.try_component(entity, Health):
                if health.value <= 0:
                    states.add(StateType.Dead)
                    health.value = 0

            states_comp.value.clear()
            states_comp.value.update(states)


class StateHandlingProcessor(esper.Processor):
    def process(self, **_):
        for _, (ani, states) in self.world.get_components(Animation, States):
            states = states.value

            if StateType.Dead in states and self.world.has_component(entity, Velocity):
                self.world.remove_component(entity, Velocity)
                if ani.state_based_frames and StateType.Dead in ani.state_based_frames:
                    ani.state_based_frames[StateType.Stands] = [
                        surface.copy() for surface in ani.frames
                    ]
                    ani.frames = ani.state_based_frames[StateType.Dead]
                    ani.delay = 400 // len(ani.frames)

            for part_ent in ani.children:
                part = self.world.component_for_entity(part_ent, Part).type

                if part == PartType.Legs and StateType.Stands in states:
                    self.world.add_component(part_ent, Invisible())
                elif self.world.has_component(part_ent, Invisible):
                    self.world.remove_component(part_ent, Invisible)
