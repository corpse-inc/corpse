import sys
import esper
import pygame

from typing import Any, Tuple

import animation as ani
import creature


FPS = 60

RESOLUTION = 320, 320
CAMERA_SIZE = RESOLUTION

# TODO: Баг: при изменении данной константы система rotation.RotationProcessor
# неправильно вращает спрайты.
CAMERA_ZOOM = 1

PLAYER_SPEED = 3


def init_resources_path() -> str:
    res = "/".join(__file__.split("/")[:-2]) + "/resources"
    if sys.platform not in {"linux", "darwin"} and res.startswith("/"):
        return res[1:]
    return res


RESOURCES = init_resources_path()


class ResourcePath:
    @classmethod
    def location_tilemap(cls, location_id: str) -> str:
        return f"{RESOURCES}/locations/tilemaps/{location_id}/tilemap.tmx"

    @classmethod
    def creature_frame(cls, creature: str, state: ani.AnimationState, idx: int) -> str:
        return f"{RESOURCES}/creatures/{creature}/{state.name}/{idx}.png"


def animation_from_surface(surface: pygame.surface.Surface) -> ani.Animation:
    return ani.Animation(
        state=(ani.AnimationState.Stands,),
        frames={
            (ani.AnimationState.Stands,): (surface,),
        },
    )


def surface_from_animation(animation: ani.Animation) -> pygame.surface.Surface:
    return animation.frames[animation.state][animation.frame_idx]


def location_map_size(location) -> tuple[int, int]:
    if location.__class__.__name__ != "Location":
        raise TypeError("Object of type Location expected")

    map = location.map
    w, h, tile = map.width, map.height, map.tilewidth
    return w * tile, h * tile


def sprite(
    image: pygame.surface.Surface, rect: pygame.rect.Rect
) -> pygame.sprite.Sprite:
    sprite = pygame.sprite.Sprite()
    sprite.image = image
    sprite.rect = rect
    return sprite


def player(processor, *components) -> Tuple[Any] | Any | int:
    world: esper.World = processor.world
    if len(components) == 1:
        return world.get_components(creature.PlayerMarker, *components)[0][1][1]
    elif len(components) != 0:
        return world.get_components(creature.PlayerMarker, *components)[0][1][1:]
    else:
        return world.get_component(creature.PlayerMarker)[0][0]
