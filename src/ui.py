import pygame_gui
import pygame
import esper

from dataclasses import dataclass as component


class UiDrawingProcessor(esper.Processor):
    def process(self, dt=None, screen=None, uimanager=None, **_):
        ui: pygame_gui.UIManager = uimanager

        for event in pygame.event.get():
            ui.process_events(event)

        ui.draw_ui(screen)
        ui.update(dt / 1000)
