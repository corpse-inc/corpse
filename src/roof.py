import esper
import utils

from render import Collision
from object import Invisible

from dataclasses import dataclass as component


@component
class Roof:
    pass


class RoofTogglingProcessor(esper.Processor):
    def process(self, **_):
        if not (player_collision := utils.get.player(self, Collision)):
            return

        for roof, _ in self.world.get_component(Roof):
            if roof in player_collision.entities:
                self.world.add_component(roof, Invisible())
            elif self.world.try_component(roof, Invisible):
                self.world.remove_component(roof, Invisible)
