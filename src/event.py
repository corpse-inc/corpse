import esper
import utils
import pygame
import pygame_gui

from movement import Velocity
from creature import PlayerMarker
from utils.consts import SLOT_KEYS
from item import CollidedItem, Equipment, Inventory, TakeItemRequest, GroundItem

from typing import Optional
from dataclasses import dataclass as component


@component
class EventProcessingLock:
    ms: int
    _ms: Optional[int] = None


class EventProcessor(esper.Processor):
    """Обрабатывает события."""

    def _handle_key_press(self, paused, settings, wheel_up, wheel_down):
        unlocked = len(self.world.get_component(EventProcessingLock)) == 0
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_ESCAPE]:
            paused[0] = True
            return

        if (
            pressed[pygame.K_LCTRL]
            and (pressed[pygame.K_EQUALS] or pressed[pygame.K_PLUS])
            or pressed[pygame.K_LCTRL]
            and wheel_up
        ) and settings["zoom"] < utils.consts.MAX_ZOOM:
            settings["zoom"] += utils.consts.ZOOM_STEP
        elif (
            pressed[pygame.K_LCTRL]
            and pressed[pygame.K_MINUS]
            or pressed[pygame.K_LCTRL]
            and wheel_down
        ) and settings["zoom"] > utils.consts.MIN_ZOOM:
            settings["zoom"] -= utils.consts.ZOOM_STEP

        vel = utils.get.player(self, Velocity)

        if vel:
            if pressed[pygame.K_w]:
                vel.vector.y = -vel.value
            if pressed[pygame.K_a]:
                vel.vector.x = -vel.value
            if pressed[pygame.K_s]:
                vel.vector.y = vel.value
            if pressed[pygame.K_d]:
                vel.vector.x = vel.value

        if (
            unlocked
            and (inv := utils.get.player(self, Inventory))
            and (equip := utils.get.player(self, Equipment))
        ):
            if pressed[pygame.K_LCTRL]:
                for i, slot_key in enumerate(SLOT_KEYS):
                    if pressed[slot_key] and equip.item != i:
                        inv.slots[i], inv.slots[equip.item] = (
                            inv.slots[equip.item],
                            inv.slots[i],
                        )
                        self.world.create_entity(EventProcessingLock(200))
                        break
            else:
                for i, slot_key in enumerate(SLOT_KEYS):
                    if pressed[slot_key]:
                        equip.item = i

    def _handle_key_release(self, event: pygame.event.Event):
        for _, (_, vel) in self.world.get_components(PlayerMarker, Velocity):
            if event.key in {pygame.K_w, pygame.K_s}:
                vel.vector.y = 0
            elif event.key in {pygame.K_a, pygame.K_d}:
                vel.vector.x = 0

    def process(
        self,
        running=None,
        uimanager=None,
        paused=None,
        events=None,
        settings=None,
        dt=None,
        **_,
    ):
        ui: pygame_gui.UIManager = uimanager

        wheel_up = False
        wheel_down = False

        for ent, lock in self.world.get_component(EventProcessingLock):
            if lock._ms is None:
                lock._ms = lock.ms
            lock._ms -= dt
            if lock._ms <= 0:
                self.world.remove_component(ent, EventProcessingLock)

        for event in events:
            ui.process_events(event)

            match event.type:
                case pygame.QUIT:
                    if running is not None:
                        running[0] = False
                        break
                    else:
                        pygame.quit()
                case pygame.KEYDOWN:
                    if not (player := utils.get.player(self)):
                        break

                    if event.key == pygame.K_e and (
                        item := self.world.try_component(player, CollidedItem)
                    ):
                        self.world.add_component(player, TakeItemRequest(item.entity))
                    elif event.key == pygame.K_q:
                        self.world.add_component(
                            player,
                            GroundItem(
                                self.world.component_for_entity(player, Equipment).item
                            ),
                        )

                case pygame.KEYUP:
                    self._handle_key_release(event)

                case pygame.MOUSEWHEEL:
                    if event.y > 0:
                        wheel_up = True
                    elif event.y < 0:
                        wheel_down = True

                case pygame_gui.UI_BUTTON_PRESSED:
                    if not (player := utils.get.player(self)):
                        break

                    if event.ui_object_id.startswith("slot") and (
                        equip := self.world.try_component(player, Equipment)
                    ):
                        slot = int(event.ui_object_id.split("slot")[-1]) - 1
                        equip.item = slot

        self._handle_key_press(paused, settings, wheel_up, wheel_down)
