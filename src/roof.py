import esper
import pygame
import utils

from render import Sprite
from object import Invisible
from location import Layer, Position


class RoofTogglingProcessor(esper.Processor):
    def process(self, **_):
        if not (player_render := utils.get.player(self, Sprite).sprite):
            return

        for roof, (render, pos) in self.world.get_components(Sprite, Position):
            roof_render = render.sprite

            if pos.layer != Layer.Roofs or roof_render is None:
                continue

            if pygame.sprite.collide_mask(player_render, roof_render):
                self.world.add_component(roof, Invisible())
            elif self.world.try_component(roof, Invisible):
                self.world.remove_component(roof, Invisible)
