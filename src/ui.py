import esper
import utils
import pygame
import pygame_gui

from typing import Dict
from animation import Animation

from meta import About, Id
from item import CollidedItem, Equipment, Inventory
from utils.consts import (
    INV_SLOT_PADDING,
    INV_SLOT_SIZE,
    INV_SLOT_WIDTH,
    INV_SLOT_HEIGHT,
    SLOT_BUTTON_NORMAL_BORDER_COLOR,
    SLOT_BUTTON_SELECTED_BORDER_COLOR,
)

from dataclasses import dataclass as component


class UiMakingProcessor(esper.Processor):
    def process(self, uimanager=None, uistorage=None, screen=None, dt=None, **_):
        if not (player := utils.get.player(self)):
            return

        ui: pygame_gui.UIManager = uimanager
        elems: Dict[str, pygame_gui.core.ui_element.UIElement] = uistorage

        sw, sh = screen.get_rect().size

        if "tooltips" not in elems:
            elems["tooltips"] = {}

        if (inv := self.world.try_component(player, Inventory)) and (
            equip := self.world.try_component(player, Equipment)
        ):
            row_width = INV_SLOT_WIDTH * inv.capacity

            if "inventory" not in elems:
                elems["inventory"] = {
                    (i + 1): {"button": None, "icon": None} for i in range(inv.capacity)
                }

            # Всплывающая подсказка для взятия предмета.
            if item := self.world.try_component(player, CollidedItem):
                about = self.world.component_for_entity(item.entity, About)
                elems["tooltips"]["take_item"] = ui.create_tool_tip(
                    f"Взять <i>{about.name}</i> (<b>E</b>)", (sw / 2 - 50, 20), (0, 0)
                )

            for i in range(1, inv.capacity + 1):
                item = inv.slots[i - 1]

                slot = elems["inventory"][i]

                # Слот
                if not slot["button"]:
                    position = (
                        (i - 1) * INV_SLOT_WIDTH + sw / 2 - row_width / 2,
                        sh - INV_SLOT_HEIGHT,
                    )
                    relative_rect = pygame.Rect(position, INV_SLOT_SIZE)
                    slot["button"] = pygame_gui.elements.UIButton(relative_rect, "", ui)

                button = slot["button"]

                # Меняем стиль кнопки, если она указывает на текущий выбранный
                # предмет
                if equip.item == (i - 1):
                    button.colours["normal_border"] = SLOT_BUTTON_SELECTED_BORDER_COLOR
                    button.rebuild()
                elif (
                    button.colours["normal_border"] == SLOT_BUTTON_SELECTED_BORDER_COLOR
                ):
                    button.colours["normal_border"] = SLOT_BUTTON_NORMAL_BORDER_COLOR
                    button.rebuild()

                # Иконка предмета в слоте
                if item is not None:
                    ani = self.world.component_for_entity(item, Animation)
                    surface = utils.convert.surface_from_animation(ani)

                    if not slot["icon"]:
                        bx, by = button.get_relative_rect().topleft
                        position = (bx + INV_SLOT_PADDING, by + INV_SLOT_PADDING)
                        relative_rect = pygame.Rect(
                            position,
                            (
                                INV_SLOT_WIDTH - INV_SLOT_PADDING * 2,
                                INV_SLOT_HEIGHT - INV_SLOT_PADDING * 2,
                            ),
                        )

                        slot["icon"] = pygame_gui.elements.UIImage(
                            relative_rect, surface, ui
                        )
                    elif slot["icon"].image != surface:
                        slot["icon"].set_image(surface)
                elif slot["icon"]:
                    slot["icon"].kill()
                    slot["icon"] = None

                # Всплывающая подсказка, показывающая информацию о предмете при
                # наведении курсора мыши на слот.
                if item is not None and button.check_hover(dt, False):
                    text = ""

                    if about := self.world.try_component(item, About):
                        text = f"<i>{about.name}</i>"
                        if about.description:
                            text += f"<br><br>{about.description}"
                    else:
                        text = self.world.component_for_entity(item, Id).id

                    elems["tooltips"]["item_info"] = ui.create_tool_tip(
                        text, pygame.mouse.get_pos(), (0, -INV_SLOT_HEIGHT)
                    )


class UiDrawingProcessor(esper.Processor):
    """Рисует и обновляет элементы ui."""

    def process(self, dt=None, screen=None, uimanager=None, uistorage=None, **_):
        ui: pygame_gui.UIManager = uimanager
        elems: Dict[str, pygame_gui.core.ui_element.UIElement] = uistorage

        ui.draw_ui(screen)
        ui.update(dt / 1000)

        for tooltip in elems["tooltips"].values():
            tooltip.kill()
            del tooltip
