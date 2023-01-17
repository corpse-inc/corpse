import utils
import esper
import pygame

from enum import IntEnum, auto
from typing import Any, Optional, Sequence, Tuple
from dataclasses import dataclass as component
from dataclasses import dataclass


@component
class Enemy:
    """Компонент, обозначающий факт вражды между данным существом и entity."""

    entity: int


class EnemyRoutingProcessor(esper.Processor):
    """Маршрутизирует враждебных существ."""

    def process(self, **_):
        from location import Position
        from object import BumpMarker
        from movement import Velocity, Direction

        for ent, (enemy, pos, vel) in self.world.get_components(
            Enemy, Position, Velocity
        ):
            if (ins := self.world.try_component(ent, FollowInstructions)) and (
                (dir := self.world.try_component(ent, Direction))
                and ins._current
                and ins._current.cmd in {Cmd.StepBackward, Cmd.StepForward}
            ):
                vec = utils.math.angle_vector(dir.angle) * vel.value / 2
                if ins._current.cmd == Cmd.StepForward:
                    vel.vector = vec
                elif ins._current.cmd == Cmd.StepBackward:
                    vel.vector = -vec
                ins._consumed = 1
                continue

            if self.world.has_component(ent, FollowInstructions):
                vel.vector = pygame.Vector2(0)
                vel.angle = 0
                continue

            enemy_pos = self.world.component_for_entity(enemy.entity, Position)
            ex, ey = enemy_pos.coords
            x, y = pos.coords

            if ex < x:
                vel.vector.x = -vel.value
            elif ex > x:
                vel.vector.x = vel.value

            if ey < y:
                vel.vector.y = -vel.value
            elif ey > y:
                vel.vector.y = vel.value

            if object := self.world.try_component(ent, BumpMarker):
                self.world.add_component(
                    ent,
                    FollowInstructions(
                        (Command(Cmd.StepBackward, 5),)
                        if object.entity == enemy.entity
                        else (
                            Command(Cmd.StepBackward, 10),
                            Command(Cmd.Rotate, 70),
                            Command(Cmd.StepForward, 50),
                        )
                    ),
                )


class EnemyRotationProcessor(esper.Processor):
    """Поворачивает враждебных существ."""

    def process(self, **_):
        from location import Position
        from movement import Direction

        for ent, (enemy, dir, pos) in self.world.get_components(
            Enemy, Direction, Position
        ):
            if (
                (ins := self.world.try_component(ent, FollowInstructions))
                and ins._current
                and ins._current.cmd == Cmd.Rotate
            ):
                consume = ins._current.cons / 10
                dir.angle += consume
                dir.vector = None
                ins._consumed = consume
                continue

            if self.world.has_component(ent, FollowInstructions):
                continue

            enemy_pos = self.world.component_for_entity(enemy.entity, Position)

            dir.vector = enemy_pos.coords - pos.coords


class Cmd(IntEnum):
    Rotate = auto()
    StepForward = auto()
    StepBackward = auto()
    Freeze = auto()


@dataclass
class Command:
    cmd: Cmd
    args: Sequence[Any]
    cons: Optional[float] = None  # consumption data


@component
class FollowInstructions:
    commands: Sequence[Cmd]
    _cmds = None
    _consumed: float = 0
    _current: Optional[Command] = None
    _lastpop: bool = False


@dataclass
class _InnerCmd:
    cmd: Command
    consumed: float


class InstructingProcessor(esper.Processor):
    def process(self, **_):
        for ent, ins in self.world.get_component(FollowInstructions):
            if ins._cmds is None:
                for cmd in ins.commands:
                    if cmd.cons is None:
                        cmd.cons = cmd.args
                ins._cmds = [_InnerCmd(cmd, 0) for cmd in reversed(ins.commands)]

            cmds = ins._cmds

            _current = ins._cmds[-1]
            ins._current = _current.cmd

            if not ins._lastpop:
                if ins._current.cons > 0:
                    _current.consumed += ins._consumed
                else:
                    _current.consumed -= ins._consumed

            ins._consumed = 0
            ins._lastpop = False

            if abs(_current.consumed) >= abs(ins._current.cons):
                cmds.pop()
                ins._lastpop = True
                ins._consumed = 0

            if len(cmds) == 0:
                self.world.remove_component(ent, FollowInstructions)
                continue
