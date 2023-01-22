import pygame

DEFAULT_SETTINGS = {
    "resolution": (640, 480),
    "zoom": 1.0,
}

FPS = 60

# Скорость существ по умолчанию.
DEFAULT_SPEED = 3

# За сколько пикселей до подхода к границам карты запрещать проходить дальше.
TILEMAP_BOUNDS = 32

MAX_ZOOM = 5.0
MIN_ZOOM = 1.0
ZOOM_STEP = 0.1

DEFAULT_CONSUME_SIZE = False
DEFAULT_CONSUME_IMAGE = True

# Размер слотов инвентаря.
INV_SLOT_WIDTH = 32 + 16
INV_SLOT_HEIGHT = INV_SLOT_WIDTH
INV_SLOT_SIZE = INV_SLOT_WIDTH, INV_SLOT_HEIGHT

# Внутренний отступ слотов.
INV_SLOT_PADDING = 8

SLOT_BUTTON_NORMAL_BORDER_COLOR = pygame.Color(92, 96, 98, 255)
SLOT_BUTTON_SELECTED_BORDER_COLOR = pygame.Color(0, 50, 0, 200)

SLOT_KEYS = (
    pygame.K_1,
    pygame.K_2,
    pygame.K_3,
    pygame.K_4,
    pygame.K_5,
)
