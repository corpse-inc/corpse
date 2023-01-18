import esper
import utils
import pygame_gui

from meta import About
from creature import Health
from item import CollidedItem

from dataclasses import dataclass as component


@component
class UiElement:
    element: pygame_gui.core.ui_element.UIElement


class UiDrawingProcessor(esper.Processor):
    """Рисует и обеовляет элементы ui, проверяет события, связанные с ui."""

    def process(self, dt=None, screen=None, uimanager=None, **_):
        ui: pygame_gui.UIManager = uimanager

        player, health = utils.get.player(self, Health, id=True)
        sw, sh = screen.get_rect().size

        # health_tt = ui.create_tool_tip(f"{health.value}", (20, 20), (0, 0))

        if item := self.world.try_component(player, CollidedItem):
            about = self.world.component_for_entity(item.entity, About)
            take_item_tt = ui.create_tool_tip(
                f"Взять <i>{about.name}</i> (<b>E</b>)", (sw / 2 - 50, 20), (0, 0)
            )

        ui.draw_ui(screen)
        ui.update(dt / 1000)

        # health_tt.kill()
        if item:
            take_item_tt.kill()
