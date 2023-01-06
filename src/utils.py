import os
import sys
import math
import esper
import pygame

from typing import Callable, Iterable, Optional
from animation import StateType
from location import Position, SpawnPoint

FPS = 60

RESOLUTION = 640, 640
CAMERA_SIZE = RESOLUTION

# TODO: Баг: при изменении данной константы система rotation.RotationProcessor
# неправильно вращает спрайты.
CAMERA_ZOOM = 1

PLAYER_SPEED = 3

_cache = {}


def init_resources_path() -> str:
    res = "/".join(__file__.split("/")[:-2]) + "/data"
    if sys.platform not in {"linux", "darwin"} and res.startswith("/"):
        return res[1:]
    return res


RESOURCES = init_resources_path()


class ResourcePath:
    @classmethod
    def location_tilemap(cls, location_id: str) -> str:
        return f"{RESOURCES}/world/{location_id}.tmx"

    @classmethod
    def frame(
        cls,
        object_id: str,
        part_type: Optional[str] = None,
        part_state: Optional[str] = None,
        idx: Optional[int] = None,
    ) -> str:
        s = f"{RESOURCES}/frames/{object_id}"

        if part_type:
            s += f"/{part_type}"

        if part_state:
            s += f"/{part_state}"

        if idx:
            return f"{s}/{idx}.png"

        return s


def animation_from_surface(surface: pygame.surface.Surface):
    from animation import Animation

    return Animation(frames=(surface,))


def surface_from_animation(animation) -> pygame.surface.Surface:
    return animation.frames[animation._frame]


def location_map_size(location) -> tuple[int, int]:
    if location.__class__.__name__ != "Location":
        raise TypeError("Object of type Location expected")

    map = location.map
    w, h, tile = map.width, map.height, map.tilewidth
    return w * tile, h * tile


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


def player(processor, *components, id=False, cache=True):
    from creature import PlayerMarker

    world: esper.World = processor.world

    if id and cache:
        key = "player_entity_id"

    if len(components) == 1:
        comps = world.get_components(PlayerMarker, *components)[0]

        if cache and id and _cache.get(key, None) is None:
            _cache[key] = comps[0]

        return (comps[0], comps[1][1]) if id else comps[1][1]
    elif len(components) != 0:
        comps = world.get_components(PlayerMarker, *components)[0]

        if cache and id and _cache.get(key, None) is None:
            _cache[key] = comps[0]

        return (comps[0], comps[1][1:]) if id else comps[1][1:]
    elif cache:
        if _cache.get(key, None) is None:
            _cache[key] = world.get_component(PlayerMarker)[0][0]

        return _cache[key]


def player_from_world(world, *components, id=False):
    fake_processor = esper.Processor()
    fake_processor.world = world
    return player(fake_processor, *components, id=id, cache=False)


def location(processor, id=False):
    """Возвращает id сущности локации и компонент локации в виде кортежа."""

    from location import Location

    world: esper.World = processor.world

    entity, location = world.get_component(Location)[0]

    if id:
        return entity, location

    return location


def solid_group(processor):
    from object import SolidGroup

    world: esper.World = processor.world
    for _, group in world.get_component(SolidGroup):
        return group

def items_group(processor):
    from items import ItemsGroup

    world: esper.World = processor.world
    for _, group in world.get_component(ItemsGroup):
        return group


def time(processor, cache=True):
    from chrono import Time

    world: esper.World = processor.world

    if cache:
        key = "time_entity_id"

        if time := _cache.get(key, None):
            return world.component_for_entity(time, Time)

        comp = world.get_component(Time)
        _cache[key] = comp[0][0]
        return comp[0][1]

    return world.get_component(Time)[0]


def vector_angle(vector: pygame.Vector2) -> float:
    return vector.as_polar()[1]


def snake_to_camel_case(snake_case_string: str) -> str:
    return "".join(c.title() for c in snake_case_string.split("_"))


def rotate_point(origin, point, angle):
    """Поворачивает точку (point) против часовой стрелки на заданный в градусах
    угол (angle) вокруг заданной точки (origin)."""

    angle = math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)

    return qx, qy


# clamp(x) = max(a,min(x,b)) ∈ [a,b]
def clamp(x, a, b):
    """Сжимает число x в промежуток [a, b]."""
    return max(a, min(x, b))


def dir_count(dir: str) -> int:
    """Возвращает количество файлов в директории."""
    return len(next(os.walk(dir))[2])


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
    from bind import BindRequest
    from render import Renderable
    from creature import Creature
    from movement import Direction, Velocity
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
        Direction(),
        Renderable(),
        Velocity(pygame.Vector2(0)),
        States(states),
        Animation(tuple(frames)),
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
            Renderable(),
            Part(creature, PartType.from_str(part)),
        )

        world.create_entity(BindRequest(creature, part_id, Position))
        world.create_entity(BindRequest(creature, part_id, Direction))

        parts.append(part_id)

    world.component_for_entity(creature, Animation).children = tuple(parts)

    return creature
