import esper
import utils

from render import Sprite


class CameraProcessor(esper.Processor):
    """Центрирует камеру на игрока."""

    def process(self, **_):
        if render := utils.get.player(self, Sprite):
            location = utils.get.location(self)
            location.sprites.center(render.sprite.rect.center)
