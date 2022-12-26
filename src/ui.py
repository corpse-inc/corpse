import pygame_gui
import esper

from dataclasses import dataclass as component


@component
class UiElement:
    element: pygame_gui.core.ui_element.UIElement


class UiDrawingProcessor(esper.Processor):
    """Рисует и обеовляет элементы ui, проверяет события, связанные с ui."""

    def process(self, dt=None, screen=None, uimanager=None, **_):
        ui: pygame_gui.UIManager = uimanager

        ui.draw_ui(screen)
        ui.update(dt / 1000)
