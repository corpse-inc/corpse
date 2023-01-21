import esper
import utils


class CameraProcessor(esper.Processor):
    """Центрирует камеру на игрока."""

    def process(self, **_):
        from render import Renderable

        render = utils.get.player(self, Renderable)
        location = utils.get.location(self)

        if render.sprite is not None:
            location.sprites.center(render.sprite.rect.center)
