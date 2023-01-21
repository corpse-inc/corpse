from typing import Optional
import esper
import pygame
import utils

from dataclasses import dataclass as component

from creature import DamagedMarker, Health

EFFECT_DELAY = 350


@component
class ReddingEffect:
    delay: int
    _delay: Optional[int] = None


class ScreenReddingProcessor(esper.Processor):
    """Покраснение экрана."""

    def _dim(self, screen, alpha):
        darken = pygame.Surface(screen.get_size())
        darken.fill((255, 0, 0))
        darken.set_alpha(alpha)
        screen.blit(darken, (0, 0))

    def process(self, screen=None, dt=None, **_):
        player = utils.get.player(self, id=True)

        if len(
            self.world.get_component(ReddingEffect)
        ) == 0 and not self.world.has_component(player, DamagedMarker):
            health = self.world.component_for_entity(player, Health)
            if (health.value / health.max * 100) < 20:
                self._dim(screen, 200)
            return

        if len(self.world.get_component(ReddingEffect)) == 0:
            self.world.create_entity(ReddingEffect(EFFECT_DELAY))

        ent, effect = self.world.get_component(ReddingEffect)[0]

        if effect._delay is None:
            effect._delay = effect.delay

        effect._delay -= dt

        if effect._delay <= 0:
            self.world.remove_component(ent, ReddingEffect)
            return

        g = effect.delay - effect._delay
        d = effect.delay
        alpha = -1 / (d * 12) * g**2 + 1 / 12 * g + 25 / 2

        self._dim(screen, alpha)
