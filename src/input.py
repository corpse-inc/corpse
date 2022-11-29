import pygame
import esper
from creature import PlayerMarker

from movement import Velocity
from utils import PLAYER_SPEED


class InputProcessor(esper.Processor):
    """Обрабатывает события ввода с клавиатуры, мыши и т. п."""

    def _handle_key_press(self, event: pygame.event.Event):
        for _, (_, vel) in self.world.get_components(PlayerMarker, Velocity):
            match event.key:
                case pygame.K_w:
                    vel.vector.y = -PLAYER_SPEED
                case pygame.K_a:
                    vel.vector.x = -PLAYER_SPEED
                case pygame.K_s:
                    vel.vector.y = PLAYER_SPEED
                case pygame.K_d:
                    vel.vector.x = PLAYER_SPEED

    def _handle_key_release(self, event: pygame.event.Event):
        for _, (_, vel) in self.world.get_components(PlayerMarker, Velocity):
            if event.key in {pygame.K_w, pygame.K_s}:
                vel.vector.y = 0
            elif event.key in {pygame.K_a, pygame.K_d}:
                vel.vector.x = 0

    def process(self, dt, screen, running):
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running[0] = False
                case pygame.KEYDOWN:
                    self._handle_key_press(event)
                case pygame.KEYUP:
                    self._handle_key_release(event)
