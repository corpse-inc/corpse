import pygame

FPS = 60
RESOLUTION = 720, 480


if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode(RESOLUTION)
    pygame.display.set_caption("Corpse inc.")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(FPS)

    pygame.quit()
