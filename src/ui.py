import pygame
import esper

from dataclasses import dataclass as component


@component
class UiElement:
    surface: pygame.surface.Surface
    position: pygame.math.Vector2


<<<<<<< Updated upstream
=======
@component
class HintRequest:
    text: str


class HintMakingProcessor(esper.Processor):
    def process(self, **_):
        for ui, hint in self.world.get_component(HintRequest):
            font = pygame.font.Font(None, 20)
            text = font.render(hint.text, True, (0, 0, 0))
            textpos = 4, 4

            background = pygame.Surface((text.get_width() + 8, text.get_height() + 8))
            background.fill((255, 255, 255))
            pygame.draw.rect(
                background,
                (0, 0, 0),
                (0, 0, background.get_width(), background.get_height()),
                2,
            )

            background.blit(text, textpos)

            self.world.add_component(
                ui, UiElement(background, pygame.Vector2(200, 200))
            )


>>>>>>> Stashed changes
class UiDrawingProcessor(esper.Processor):
    def process(self, screen=None, **_):
        for _, elem in self.world.get_component(UiElement):
            screen.blit(elem.surface, elem.position)
