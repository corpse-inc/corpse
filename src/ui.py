import esper
from animation import Animation
import utils
import pygame
import pygame_gui

from meta import About, Id
from creature import Health
from item import CollidedItem, Inventory

from dataclasses import dataclass as component


@component
class UiElement:
    element: pygame_gui.core.ui_element.UIElement


class UiDrawingProcessor(esper.Processor):
    """Рисует и обеовляет элементы ui, проверяет события, связанные с ui."""

    def process(self, dt=None, screen=None, uimanager=None, **_):
        ui: pygame_gui.UIManager = uimanager

        player, inv = utils.get.player(self, Inventory, id=True)

        sw, sh = screen.get_rect().size

        if item := self.world.try_component(player, CollidedItem):
            about = self.world.component_for_entity(item.entity, About)
            take_item_tt = ui.create_tool_tip(
                f"Взять <i>{about.name}</i> (<b>E</b>)", (sw / 2 - 50, 20), (0, 0)
            )

        slot_width = 32 + 16
        slot_height = slot_width
        row_width = slot_width * inv.capacity
        kill = []
        for i in range(1, inv.capacity + 1):
            item = inv.slots[i - 1]

            position = ((i - 1) * slot_width + sw / 2 - row_width / 2, sh - slot_height)
            relative_rect = pygame.Rect(position, (slot_width, slot_height))
            button = pygame_gui.elements.UIButton(relative_rect, "", ui)

            if item is not None:
                padding = 8
                position = (position[0] + padding, position[1] + padding)
                relative_rect = pygame.Rect(
                    position, (slot_width - padding * 2, slot_height - padding * 2)
                )
                ani = self.world.component_for_entity(item, Animation)
                icon = pygame_gui.elements.UIImage(relative_rect, ani.frames[0], ui)
                kill.append(icon)

            kill.append(button)

        ui.draw_ui(screen)
        ui.update(dt / 1000)

        for element in kill:
            element.kill()

        if item:
            take_item_tt.kill()
