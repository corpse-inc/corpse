import esper
import pygame
import utils

FPS = 60
RESOLUTION = 720, 480


class WorldInitializer:
    def __init__(self):
        world = esper.World()

        world.add_entity(self._create_object_entities())
        world.add_entity(self._create_ui_entities())

        return world

    def _create_decoration_objects(self):
        pass

    def _create_building_objects(self):
        pass

    def _create_animate_objects(self):
        pass

    def _create_object_entities(self):
        return utils.flatten_list(
            (
                self._create_decoration_objects(),
                self._create_building_objects(),
                self._create_animate_objects(),
            )
        )

    def _create_inventory_ui(self):
        pass

    def _create_bag_ui(self):
        pass

    def _create_stats_ui(self):
        pass

    def _create_craft_ui(self):
        pass

    def _create_dialog_ui(self):
        pass

    def _create_ui_entities(self):
        return utils.flatten_list(
            (
                self._create_inventory_ui(),
                self._create_bag_ui(),
                self._create_stats_ui(),
                self._create_craft_ui(),
                self._create_dialog_ui()
            )
        )


class Game:
    def __init__(self, window, world=None):
        self.window = window
        self.world = world

    def tick(self):
        self.clock.tick_busy_loop(FPS)

    def run(self):
        self.clock = pygame.time.Clock()
        pygame.key.set_repeat(1, 1)

        if self.world is None:
            self.world = WorldInitializer()

        running = True
        while running:
            self.tick()


if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode(RESOLUTION)
    pygame.display.set_caption("Corpse inc.")

    Game(window).run()

    pygame.quit()