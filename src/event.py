import pygame
import esper
import sys

import pygame_gui

from movement import Velocity
from creature import PlayerMarker

from utils.consts import PLAYER_SPEED


class EventProcessor(esper.Processor):
    """Обрабатывает события."""

    def _handle_key_press(self, paused):
        for _, (_, vel) in self.world.get_components(PlayerMarker, Velocity):
            pressed = pygame.key.get_pressed()

            if pressed[pygame.K_ESCAPE]:
                paused[0] = True

            if pressed[pygame.K_w]:
                vel.vector.y = -PLAYER_SPEED
            if pressed[pygame.K_a]:
                vel.vector.x = -PLAYER_SPEED
            if pressed[pygame.K_s]:
                vel.vector.y = PLAYER_SPEED
            if pressed[pygame.K_d]:
                vel.vector.x = PLAYER_SPEED

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
                case pygame.KEYUP:
                    self._handle_key_release(event)
