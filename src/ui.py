import esper
import pygame_gui

from dataclasses import dataclass as component
from creature import Health

import utils


@component
class UiElement:
    element: pygame_gui.core.ui_element.UIElement


class UiDrawingProcessor(esper.Processor):
    """Рисует и обеовляет элементы ui, проверяет события, связанные с ui."""

    def process(self, dt=None, screen=None, uimanager=None, **_):
        ui: pygame_gui.UIManager = uimanager

        health = utils.get.player(self.world, Health).value
        tt = ui.create_tool_tip(f"{health}", (20, 20), (0, 0))

        ui.draw_ui(screen)
        ui.update(dt / 1000)

        tt.kill()
