import esper

from render import Renderable
from creature import PlayerMarker
from location import Location, Position


class CameraProcessor(esper.Processor):
    def process(self, dt, screen, running):
        for player, (_, position) in self.world.get_components(PlayerMarker, Position):
            location = self.world.component_for_entity(position.location, Location)
            location.sprites.center(
                self.world.component_for_entity(player, Renderable).sprite.rect.center
            )
