import utils
import esper
import pygame

from enum import Enum, auto
from typing import Dict, Optional, Set, Tuple
from dataclasses import dataclass as component

from ai import Enemy
from object import Invisible, Solid
from location import Layer, Position
from item import Inventory, Equipment, Gun
from render import MakeUnrenderableRequest
from creature import Creature, Damage, Health, DeadMarker, PlayerMarker
from movement import LookAfterMouseCursor, SetDirectionRequest, Velocity


class StateType(Enum):
    Dead = auto()
    Stands = auto()
    Walks = auto()
    HoldsGun = auto()
    HoldsEdgedWeapon = auto()
    Punches = auto()

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_str(cls, s: str):
        return cls[utils.convert.snake_to_camel_case(s)]


@component
class States:
    value: Set[StateType]


@component
class Animation:
    frames: Tuple[pygame.surface.Surface]
    delay: int = 0
    paused: bool = False
    children: Tuple[int] = None
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

            if ani.state_based_frames is None:
                ani.state_based_frames = {}

            if ani.children is None:
                ani.children = ()

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
                    self.world.add_component(entity, DeadMarker())
                    states.add(StateType.Dead)
                    states.add(StateType.Stands)
                    health.value = 0

            if (
                (equip := self.world.try_component(entity, Equipment))
                and (inv := self.world.try_component(entity, Inventory))
                and inv.slots
                and (item := inv.slots[equip.item])
                and (self.world.has_component(item, Gun))
            ):
                states.add(StateType.HoldsGun)

            states_comp.value = states


class StateHandlingProcessor(esper.Processor):
    def process(self, **_):
        for entity, (ani, states) in self.world.get_components(Animation, States):
            if self.world.has_component(entity, Part):
                continue

            states = states.value

            if StateType.Dead in states:
                remove_comps = (
                    Creature,
                    Velocity,
                    Solid,
                    SetDirectionRequest,
                    LookAfterMouseCursor,
                    Enemy,
                    Inventory,
                    Damage,
                )

                if pos := self.world.try_component(entity, Position):
                    pos.layer = Layer.Ground

                for comp in remove_comps:
                    if self.world.has_component(entity, comp):
                        self.world.remove_component(entity, comp)

                if ani.state_based_frames and StateType.Dead in ani.state_based_frames:
                    if StateType.Stands not in ani.state_based_frames:
                        ani.state_based_frames[StateType.Stands] = [
                            surface.copy() for surface in ani.frames
                        ]
                    dead_frames = ani.state_based_frames[StateType.Dead]
                    if ani.frames != dead_frames:
                        ani.frames = dead_frames
                    elif ani._frame == (len(dead_frames) - 1):
                        ani.paused = True
                        if not self.world.has_component(entity, PlayerMarker):
                            self.world.add_component(entity, MakeUnrenderableRequest())
                            for part in ani.children:
                                self.world.delete_entity(part)
                            self.world.delete_entity(entity)
                    ani.delay = 400 // len(ani.frames)
                else:
                    self.world.add_component(entity, MakeUnrenderableRequest())

                continue

            if StateType.HoldsGun in states:
                ani.frames = ani.state_based_frames[StateType.HoldsGun]
            elif (
                StateType.Stands in states
                and StateType.Stands in ani.state_based_frames
            ):
                ani.frames = ani.state_based_frames[StateType.Stands]

            for part_ent in ani.children:
                part = self.world.component_for_entity(part_ent, Part).type

                if part == PartType.Legs and StateType.Stands in states:
                    self.world.add_component(part_ent, Invisible())
                elif self.world.has_component(part_ent, Invisible):
                    self.world.remove_component(part_ent, Invisible)
