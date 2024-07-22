import esper
import utils
import pygame
import pygame_menu

from pygame_menu import Menu

from meta import Id
from creature import DeadMarker, PlayerMarker


class MenuCreationProcessor(esper.Processor):
    def process(
        self,
        world=None,
        current_menu=None,
        settings=None,
        started=None,
        paused=None,
        **_,
    ):
        dead = len(world.get_components(PlayerMarker, DeadMarker)) > 0

        if (
            not dead
            and utils.get.menu(self, "main_menu")
            and utils.get.menu(self, "pause_menu")
            and utils.get.menu(self, "settings_menu")
        ):
            return

        for ent, _ in self.world.get_component(Menu):
            self.world.delete_entity(ent)

        def open_main_menu():
            started[0] = False
            paused[0] = False
            current_menu[0] = "main_menu"
            pause_menu.select_widget(pause_menu_continue_button)

        settings_menu = Menu(
            "Corpse inc. -> Настройки",
            *settings["resolution"],
            enabled=False,
            theme=utils.make.settings_menu_theme(settings),
        )

        def change_resolution(_, res):
            settings["resolution"] = res
            pygame.display.set_mode(res)
            self.world.clear_database()

        settings_menu.add.button("Выйти в главное меню", open_main_menu)
        settings_menu.add.dropselect(
            "Разрешение экрана",
            [("640x480", (640, 480)), ("720x480", (720, 480))],
            placeholder="x".join(map(str, settings["resolution"])),
            onreturn=change_resolution,
        )

        if dead:
            main_menu = Menu(
                "Мёртв",
                *settings["resolution"],
                center_content=True,
                theme=utils.make.main_menu_dead_theme(settings),
            )
        else:
            main_menu = Menu(
                "Corpse inc.",
                *settings["resolution"],
                center_content=False,
                theme=utils.make.main_menu_theme(settings),
            )

        def play():
            started[0] = True
            self.world.clear_cache()
            self.world.clear_database()

        def open_settings():
            current_menu[0] = "settings_menu"

        if not dead:
            main_menu.add.button("Играть", play)
            main_menu.add.button("Настройки", open_settings)

        main_menu.add.button("Выйти", pygame_menu.events.EXIT)

        pause_menu = Menu(
            "",
            *settings["resolution"],
            center_content=False,
            enabled=False,
            theme=utils.make.pause_menu_theme(settings),
        )

        def continue_game():
            paused[0] = False

        pause_menu_continue_button = pause_menu.add.button(
            "Продолжить игру", continue_game
        )
        pause_menu.add.button("Выйти в главное меню", open_main_menu)

        menus = (
            ("main_menu", main_menu),
            ("settings_menu", settings_menu),
            ("pause_menu", pause_menu),
        )
        for id, menu in menus:
            menu._id = id
            self.world.create_entity(Id(id), menu)


class MenuTogglingProcessor(esper.Processor):
    def process(self, current_menu=None, paused=None, started=None, **_):
        main_menu = utils.get.menu(self, "main_menu")
        pause_menu = utils.get.menu(self, "pause_menu")
        settings_menu = utils.get.menu(self, "settings_menu")

        if not started[0] and not main_menu.is_enabled():
            main_menu.enable()
            pause_menu.disable()
        elif started[0]:
            main_menu.disable()

        if paused[0] and not pause_menu.is_enabled():
            pause_menu.enable()
            main_menu.disable()
        elif not paused[0]:
            pause_menu.disable()

        if current_menu[0] == "settings_menu":
            main_menu.disable()
            pause_menu.disable()
            settings_menu.enable()
        else:
            settings_menu.disable()


class MenuUpdatingProcessor(esper.Processor):
    def process(self, events=None, **_):
        for _, (id, menu) in self.world.get_components(Id, Menu):
            if menu.is_enabled():
                menu.update(events)


class MenuDrawingProcessor(esper.Processor):
    def process(self, screen=None, **_):
        for _, (id, menu) in self.world.get_components(Id, Menu):
            if menu.is_enabled():
                menu.draw(screen)
