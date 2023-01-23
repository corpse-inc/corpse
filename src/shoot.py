import esper
import utils
import pygame

from item import FireRate
from render import MakeRenderableRequest, MakeUnrenderableRequest
from ai import Cmd, Command, FollowInstructions

from dataclasses import dataclass as component


@component
class ShootRequest:
    pass


@component
class Bullet:
    owner: int


@component
class ShotMarker:
    pass


@component
class ShotLock:
    pass


class ShotDelayingProcessor(esper.Processor):
    def process(self, dt=None, **_):
        for ent, (blocker, _) in self.world.get_components(FireRate, ShotLock):
            if not blocker._delay:
                blocker._delay = blocker.delay
                continue

            if blocker._delay > 0:
                blocker._delay -= dt
            else:
                self.world.remove_component(ent, ShotLock)
                blocker._delay = blocker.delay


class ShootingProcessor(esper.Processor):
    def process(self, **_):
        from location import Layer
        from item import Gun, ITEMS
        from creature import Health
        from render import Collision
        from movement import Velocity
        from location import Position
        from movement import Direction
        from object import Size, Solid
        from animation import Animation
        from utils.fs import ResourcePath
        from creature import Damage, DamageRequest

        for ent, (_, pos, dir, size) in self.world.get_components(
            ShootRequest,
            Position,
            Direction,
            Size,
        ):
            self.world.remove_component(ent, ShootRequest)

            if not (
                (equips := utils.get.equips(self, ent))
                and not self.world.has_component(equips, ShotLock)
                and (gun := self.world.try_component(equips, Gun))
                and gun.ammo > 0
            ):
                continue

            gun.ammo -= 1

            if self.world.has_component(equips, FireRate):
                self.world.add_component(equips, ShotLock())

            damage = next(filter(lambda c: type(c) is Damage, ITEMS[gun.ammo_id])).value

            self.world.create_entity(
                Bullet(ent),
                Direction(dir.angle),
                Position(
                    pos.location,
                    pos.coords.copy()
                    + pygame.Vector2(size.w // 3, 0).rotate(dir.angle),
                    Layer.Objects,
                ),
                Velocity(
                    utils.math.angle_vector(dir.angle) * utils.consts.BULLET_SPEED
                ),
                Animation((pygame.image.load(ResourcePath.frame("bullet", idx=1)),)),
                MakeRenderableRequest(),
                Damage(damage),
                Solid(),
            )

            self.world.add_component(
                ent, FollowInstructions((Command(Cmd.Rotate, gun.recoil),))
            )

            self.world.add_component(ent, ShotMarker())

        for ent, (bullet, collision) in self.world.get_components(Bullet, Collision):
            if self.world.has_component(collision.entity, Health) and (
                damage := self.world.try_component(ent, Damage)
            ):
                self.world.create_entity(
                    DamageRequest(bullet.owner, collision.entity, damage.value)
                )
            self.world.add_component(ent, MakeUnrenderableRequest)
            self.world.delete_entity(ent)


class ShotMarkerRemovingProcessor(esper.Processor):
    def process(self, **_):
        for ent, _ in self.world.get_component(ShotMarker):
            self.world.remove_component(ent, ShotMarker)
