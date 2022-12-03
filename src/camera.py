import esper

from render import Renderable
from position import Position

import utils
import location as loc


class CameraProcessor(esper.Processor):
    """Центрирует камеру на игрока."""

    def process(self, **_):
        pos, render = utils.player(self, Position, Renderable)
        location = loc.current(self, pos)
        if render.sprite is not None:
            location.sprites.center(render.sprite.rect.center)
