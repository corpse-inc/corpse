import esper
from animation import Animation
import utils
import pygame
import pygame_gui

from meta import About, Id
from creature import DeadMarker, Health
from item import CollidedItem, Equipment, Inventory

from dataclasses import dataclass as component


@component
class UiElement:
    element: pygame_gui.core.ui_element.UIElement


class UiDrawingProcessor(esper.Processor):
    """Рисует и обеовляет элементы ui, проверяет события, связанные с ui."""

    def process(self, dt=None, screen=None, uimanager=None, **_):
        ui: pygame_gui.UIManager = uimanager

        kill = []

        player = utils.get.player(self)
        if (inv := self.world.try_component(player, Inventory)) and (
            equip := self.world.try_component(player, Equipment)
        ):
            sw, sh = screen.get_rect().size

            if item := self.world.try_component(player, CollidedItem):
                about = self.world.component_for_entity(item.entity, About)
                take_item_tt = ui.create_tool_tip(
                    f"Взять <i>{about.name}</i> (<b>E</b>)", (sw / 2 - 50, 20), (0, 0)
                )
                kill.append(take_item_tt)

            slot_width = 32 + 16
            slot_height = slot_width
            row_width = slot_width * inv.capacity
            for i in range(1, inv.capacity + 1):
                item = inv.slots[i - 1]

                position = (
                    (i - 1) * slot_width + sw / 2 - row_width / 2,
                    sh - slot_height,
                )
                relative_rect = pygame.Rect(position, (slot_width, slot_height))
                button = pygame_gui.elements.UIButton(relative_rect, "", ui)

                if equip.item == (i - 1):
                    button.colours["normal_border"] = pygame.Color(0, 50, 0, 200)
                    button.rebuild()

                if item is not None and button.check_hover(dt, False):
                    text = ""

                    if about := self.world.try_component(item, About):
                        text = f"<i>{about.name}</i>"
                        if about.description:
                            text += f"<br><br>{about.description}"
                    else:
                        text = self.world.component_for_entity(item, Id).id

                    item_info_tt = ui.create_tool_tip(
                        text, pygame.mouse.get_pos(), (0, -slot_height)
                    )
                    kill.append(item_info_tt)

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
