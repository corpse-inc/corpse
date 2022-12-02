import sys

from pyscroll.data import pygame
from animation import Animation, AnimationState


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
    def creature_frame(cls, creature: str, state: AnimationState, idx: int) -> str:
        return f"{RESOURCES}/creatures/{creature}/{state.name}/{idx}.png"


def surface_from_animation(animation: Animation) -> pygame.surface.Surface:
    return animation.frames[animation.state][animation.frame_idx]


def location_map_size(location) -> tuple[int, int]:
    if location.__class__.__name__ != "Location":
        raise TypeError

    map = location.map
    w, h, tile = map.width, map.height, map.tilewidth
    return w * tile, h * tile
