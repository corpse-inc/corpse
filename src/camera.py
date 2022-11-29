import esper

from render import Renderable
from creature import PlayerMarker
from location import Location, Position


class CameraProcessor(esper.Processor):
    """Центрирует камеру на игрока."""

    def process(self, dt, screen, running):
        for player, (_, position, render) in self.world.get_components(
            PlayerMarker, Position, Renderable
        ):
            location = self.world.component_for_entity(position.location, Location)
            if render.sprite is not None:
                location.sprites.center(render.sprite.rect.center)
