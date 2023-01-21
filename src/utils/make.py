import os
import utils
import esper
import pygame
import pygame_menu


from copy import deepcopy
from utils.fs import ResourcePath, dir_count
from typing import Optional, Callable, Iterable

from location import Position, SpawnPoint
from animation import StateType


def main_menu_theme(settings) -> pygame_menu.Theme:
    theme = pygame_menu.Theme()
    res = "x".join(map(str, settings["resolution"]))

    background = pygame_menu.baseimage.BaseImage(
        image_path=ResourcePath.get(f"ui/main_menu_background/{res}.jpg"),
        drawing_mode=pygame_menu.baseimage.IMAGE_MODE_FILL,
    )
    theme.background_color = background

    theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_TITLE_ONLY_DIAGONAL
    theme.selection_color = pygame.Color(0, 0, 0)
    theme.widget_margin = (-30, 0)
    theme.widget_offset = (0.35, 0.01)

    return theme


def settings_menu_theme(settings) -> pygame_menu.Theme:
    theme = pygame_menu.Theme()
    res = "x".join(map(str, settings["resolution"]))

    background = pygame_menu.baseimage.BaseImage(
        image_path=ResourcePath.get(f"ui/settings_menu_background/{res}.jpg"),
        drawing_mode=pygame_menu.baseimage.IMAGE_MODE_FILL,
    )
    theme.background_color = background

    theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_TITLE_ONLY_DIAGONAL
    theme.selection_color = pygame.Color(255, 255, 255)
    theme.widget_font_color = pygame.Color(0, 0, 0)

    return theme


def pause_menu_theme(settings) -> pygame_menu.Theme:
    theme = pygame_menu.Theme()
    res = "x".join(map(str, settings["resolution"]))

    background = pygame_menu.baseimage.BaseImage(
        image_path=ResourcePath.get(f"ui/pause_menu_background/{res}.jpg"),
        drawing_mode=pygame_menu.baseimage.IMAGE_MODE_FILL,
    )
    theme.background_color = background

    theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_TITLE_ONLY_DIAGONAL
    theme.selection_color = pygame.Color(255, 255, 255)
    theme.widget_font_color = pygame.Color(0, 0, 0)
    theme.widget_offset = (0, 0.5)

    return theme


def sprite(
    image: Optional[pygame.surface.Surface] = None,
    rect: Optional[pygame.rect.Rect] = None,
    mask: Optional[pygame.mask.Mask] = None,
) -> pygame.sprite.Sprite:
    sprite = pygame.sprite.Sprite()

    if image:
        sprite.image = image
    if rect:
        sprite.rect = rect
    if mask:
        sprite.mask = mask

    return sprite


def sprite_component(animation, position):
    from render import Sprite

    img = utils.convert.surface_from_animation(animation)

    sprite = utils.make.sprite(
        img,
        img.get_rect(center=position.coords),
        pygame.mask.from_surface(img),
    )

    return Sprite(img, sprite)


def creature(
    world: esper.World,
    id: str,
    position: Position | SpawnPoint,
    *extra_comps,
    extra_parts: Iterable[str] = (),
    states={StateType.Stands},
    surface_preprocessor: Optional[
        Callable[[pygame.surface.Surface], pygame.surface.Surface]
    ] = None,
):
    """Создаёт существо и возвращает id его сущности в базе данных сущностей.

    Аргументы:
    *world*: бд сущностей
    *id*: строковый уникальный идентификатор существа
    *position*: местоположение существа (location.Position)
    **extra_comps*: дополнительные компоненты для применения к сущности
    *extra_parts*: части тела существа помимо тела (body)
    *states*: текущие состояния существа
    *surface_preprocessor*: функция, переданная в качестве данного аргумента будет
    использована на каждом pygame.Surface в данной функции. Полезно, если прежде
    чем загружать картинку анимации, её нужно как-то обработать

    Примеры использования:
    ```python
    player = utils.creature(
        world,
        "player",
        Position(location, "test", pygame.Vector2(320, 320)),
        PlayerMarker(),
        extra_parts={"legs"},
        surface_preprocessor=lambda s: pygame.transform.rotate(
            pygame.transform.scale2x(s), 90
        ),
    player = utils.creature(
        world,
        "zombie",
        SpawnPoint("zombie")
    )
    ```"""

    from meta import Id
    from object import Solid
    from bind import BindRequest
    from creature import Creature, Health
    from movement import Direction, Velocity
    from render import MakeRenderableRequest
    from animation import States, Animation, Part, PartType

    def load_surface(path):
        prep = surface_preprocessor
        surf = pygame.image.load(path).convert_alpha()

        if prep:
            return prep(surf)

        return surf

    frames = []
    for i in range(dir_count(ResourcePath.frame(id, "body"))):
        frames.append(load_surface(ResourcePath.frame(id, "body", idx=i + 1)))

    creature = world.create_entity(
        Id(id),
        Creature(),
        Health(),
        Solid(),
        Direction(0),
        MakeRenderableRequest(),
        Velocity(pygame.Vector2(0)),
        States(states),
        position,
        *extra_comps,
    )

    parts = []
    for part in extra_parts:
        part_frames = []
        frame_number = dir_count(ResourcePath.frame(id, part))
        animation_delay = (
            400 // frame_number
        )  # замедляем анимацию при небольшом количестве кадров

        for i in range(frame_number):
            part_frames.append(load_surface(ResourcePath.frame(id, part, idx=i + 1)))

        part_id = world.create_entity(
            Animation(tuple(part_frames), animation_delay),
            MakeRenderableRequest(),
            Part(creature, PartType.from_str(part)),
        )

        world.create_entity(BindRequest(creature, part_id, Position))
        world.create_entity(BindRequest(creature, part_id, Direction))

        parts.append(part_id)

    state_based_frames = {}
    for dir, _, _ in os.walk(ResourcePath.frame(id)):
        name = dir.split("/")[-1]
        try:
            state_type = (
                StateType.from_str(name) if name != "body" else StateType.Stands
            )
        except KeyError:
            continue
        state_based_frames[state_type] = tuple(
            load_surface(ResourcePath.frame(id, name, idx=i + 1))
            for i in range(dir_count(ResourcePath.frame(id, name)))
        )

    world.add_component(
        creature,
        Animation(
            tuple(frames), children=tuple(parts), state_based_frames=state_based_frames
        ),
    )

    return creature


def item_comps(id: str, *extra_comps):
    from meta import Id
    from item import Item, ItemNotFoundError, ITEMS

    if id not in ITEMS:
        raise ItemNotFoundError(f"Предмет с идентификатором {id} не найден")

    return Id(id), Item(), *deepcopy(ITEMS[id]), *extra_comps


def item(world: esper.World, id: str, *extra_comps):
    from item import ItemNotFoundError, ITEMS

    if id not in ITEMS:
        raise ItemNotFoundError(f"Предмет с идентификатором {id} не найден")

    return world.create_entity(item_comps(id, *extra_comps))
