import pygame
import esper


class InputProcessor(esper.Processor):
    def process(self, dt, running):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running[0] = False
