import utils
import esper
import pygame

from enum import IntEnum, auto
from typing import Any, Optional, Sequence
from dataclasses import dataclass as component
from dataclasses import dataclass


@component
class Enemy:
    """Компонент, обозначающий факт вражды между данным существом и entity."""

    entity: int


class EnemyRoutingProcessor(esper.Processor):
    """Маршрутизирует враждебных существ."""

    def process(self, **_):
        from object import Solid
        from render import Collision
        from location import Position
        from movement import Velocity
        from creature import DeadMarker

        for ent, (enemy, pos, vel) in self.world.get_components(
            Enemy, Position, Velocity
        ):
            if self.world.has_component(ent, FollowInstructions):
                vel.vector = pygame.Vector2(0)
                vel.angle = 0
                continue

            if self.world.has_component(enemy.entity, DeadMarker):
                self.world.add_component(
                    ent,
                    FollowInstructions(
                        (
                            Command(Cmd.Rotate, 360),
                            Command(Cmd.Rotate, -360),
                            Command(Cmd.StepForward, 10),
                        )
                    ),
                )
                self.world.remove_component(ent, Enemy)
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

            if (
                object := self.world.try_component(ent, Collision)
            ) and self.world.has_component(ent, Solid):
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
        from movement import SetDirectionRequest

        for ent, (enemy, pos) in self.world.get_components(Enemy, Position):
            if self.world.has_component(ent, FollowInstructions):
                continue

            enemy_pos = self.world.component_for_entity(enemy.entity, Position)

            self.world.add_component(
                ent,
                SetDirectionRequest(
                    utils.math.vector_angle(enemy_pos.coords - pos.coords)
                ),
            )


class EnemyDamagingProcessor(esper.Processor):
    def process(self, **_):
        from render import Collision
        from creature import Damage, DamageLock, DamageRequest

        for entity, (enemy, collision, damage) in self.world.get_components(
            Enemy, Collision, Damage
        ):
            if self.world.has_component(entity, DamageLock):
                continue

            if enemy.entity == collision.entity:
                self.world.create_entity(
                    DamageRequest(entity, enemy.entity, damage.value)
                )


class InstructionExecutingProcessor(esper.Processor):
    def process(self, **_):
        from movement import Direction, Velocity

        for ent, ins in self.world.get_component(FollowInstructions):
            cur = ins._current
            cmd, args, cons = cur.cmd, cur.args, cur.cons

            if not cur:
                continue

            if (dir := self.world.try_component(ent, Direction)) and (
                (vel := self.world.try_component(ent, Velocity))
                and cmd in {Cmd.StepBackward, Cmd.StepForward}
            ):
                vec = utils.math.angle_vector(dir.angle)

                if abs(vec.x) > abs(vec.y):
                    vec.x, vec.y = vel.value if vec.x > 0 else -vel.value, 0
                else:
                    vec.x, vec.y = 0, vel.value if vec.y > 0 else -vel.value

                if cmd == Cmd.StepForward:
                    vel.vector = vec
                elif cmd == Cmd.StepBackward:
                    vel.vector = -vec

                ins._consumed = 1

                continue

            if (
                ins := self.world.try_component(ent, FollowInstructions)
            ) and cmd == Cmd.Rotate:
                consume = cons / 10
                dir.angle += consume
                dir.vector = None
                ins._consumed = consume
                continue


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
    commands: Sequence[Command]
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
