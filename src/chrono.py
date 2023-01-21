import esper
import pygame
import utils

# Сколько длится день в мс
DAY = 20 * 1000 * 60  # 20 минут

# Максимальное затемнение (не может быть больше 255)
MAX_ALPHA = 240

# Параметры анимации затемнения/осветвления экрана при смене дня/ночи.
#
# T: Период анимации затемнения в мс
# N: Количество кадров анимации затемнения
# M: Множитель затемнения на каждом кадре анимации.
T, N, M = 5, 1000, 0.24


class DayNightCyclingProcessor(esper.Processor):
    """Система смены дня и ночи."""

    def process(self, screen=None, **_):
        starttime = pygame.time.get_ticks()
        daytime = starttime % DAY

        if daytime < (DAY / 2):
            return

        alpha = utils.math.clamp(M * N, 0, MAX_ALPHA)

        night = daytime - (DAY / 2)
        for i in range(int(N)):
            if (T * (i - 1)) <= night < (T * i):
                alpha = M * i
                break

        day = DAY - daytime
        for i in range(int(N)):
            if (T * (i - 1)) <= day < (T * i):
                alpha = M * i
                break

        alpha = utils.math.clamp(alpha, 0, MAX_ALPHA)

        darken = pygame.Surface(screen.get_size())
        darken.fill((0, 0, 0))
        darken.set_alpha(alpha)
        screen.blit(darken, (0, 0))
