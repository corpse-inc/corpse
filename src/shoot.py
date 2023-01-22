import esper
from animation import Animation
from creature import Damage
from item import ITEMS
from movement import Velocity
import utils
import pygame

from dataclasses import dataclass as component

from utils.fs import ResourcePath


@component
class ShootRequest:
    pass


@component
class Bullet:
    owner: int


class ShootingProcessor(esper.Processor):
    def process(self, **_):
        from item import Gun
        from object import Size
        from location import Position
        from movement import Direction

        for ent, (_, pos, dir, size) in self.world.get_components(
            ShootRequest,
            Position,
            Direction,
            Size,
        ):
            self.world.remove_component(ent, ShootRequest)

            if not (
                (equips := utils.get.equips(self, ent))
                and (gun := self.world.try_component(equips, Gun))
                and gun.ammo > 0
            ):
                continue

            damage = next(filter(lambda c: type(c) is Damage, ITEMS[gun.ammo_id])).value

            vector = utils.math.angle_vector(dir.angle)

            self.world.create_entity(
                Bullet(ent),
                Direction(dir.angle),
                Velocity(vector, 10),
                Animation((pygame.image.load(ResourcePath.frame("bullet", idx=1)),)),
                Damage(damage),
            )
