import esper

from render import Renderable
from location import Position
from render import Renderable

import utils


class CameraProcessor(esper.Processor):
    """Центрирует камеру на игрока."""

    def process(self, **_):
        pos, render = utils.player(self, Position, Renderable)
        location = utils.location(self, pos)
        if render.sprite is not None:
            location.sprites.center(render.sprite.rect.center)
