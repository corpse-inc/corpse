import esper
import utils
import pygame

import pygame_gui

from movement import Velocity
from creature import PlayerMarker
from item import CollidedItem, Equipment, TakeItemRequest


class EventProcessor(esper.Processor):
    """Обрабатывает события."""

    def _handle_key_press(self, paused):
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_ESCAPE]:
            paused[0] = True

        vel = utils.get.player(self, Velocity)

        if pressed[pygame.K_w]:
            vel.vector.y = -vel.value
        if pressed[pygame.K_a]:
            vel.vector.x = -vel.value
        if pressed[pygame.K_s]:
            vel.vector.y = vel.value
        if pressed[pygame.K_d]:
            vel.vector.x = vel.value

    def _handle_key_release(self, event: pygame.event.Event):
        for _, (_, vel) in self.world.get_components(PlayerMarker, Velocity):
            if event.key in {pygame.K_w, pygame.K_s}:
                vel.vector.y = 0
            elif event.key in {pygame.K_a, pygame.K_d}:
                vel.vector.x = 0

    def process(self, running=None, uimanager=None, paused=None, events=None, **_):
        ui: pygame_gui.UIManager = uimanager

        self._handle_key_press(paused)

        for event in events:
            ui.process_events(event)

            match event.type:
                case pygame.QUIT:
                    if running is not None:
                        running[0] = False
                    else:
                        pygame.quit()
                case pygame.KEYDOWN:
                    player = utils.get.player(self, id=True)
                    if event.key == pygame.K_e and (
                        item := self.world.try_component(player, CollidedItem)
                    ):
                        self.world.add_component(player, TakeItemRequest(item.entity))
                    elif event.key in (
                        slot_keys := (
                            pygame.K_1,
                            pygame.K_2,
                            pygame.K_3,
                            pygame.K_4,
                            pygame.K_5,
                        )
                    ):
                        self.world.component_for_entity(
                            player, Equipment
                        ).item = slot_keys.index(event.key)

                case pygame.KEYUP:
                    self._handle_key_release(event)
