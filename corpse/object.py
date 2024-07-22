import esper
import utils

from dataclasses import dataclass as component


class SizeComputingProcessor(esper.Processor):
    def process(self, **_):
        from animation import Animation

        for ent, ani in self.world.get_component(Animation):
            self.world.add_component(
                ent, Size(*utils.convert.surface_from_animation(ani).get_size())
            )


@component
class Size:
    w: float
    h: float


@component
class Solid:
    pass


@component
class Invisible:
    pass


class ObjectNotFoundError(Exception):
    pass
