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
    if res.startswith("/"):
        return res[1:]
    return res


RESOURCES = init_resources_path()


def crossplatform_path(path: str) -> str:
    return path
    # if sys.platform == "posix" or not sys.platform.startswith("win"):
    # return path
    # return path.replace("/", "\\")


class ResourcePath:
    @classmethod
    def location_tilemap(cls, location_id: str) -> str:
        return crossplatform_path(
            f"{RESOURCES}/locations/tilemaps/{location_id}/tilemap.tmx"
        )

    @classmethod
    def creature_frame(cls, creature: str, state: AnimationState, idx: int) -> str:
        return crossplatform_path(
            f"{RESOURCES}/creatures/{creature}/{state.name}/{idx}.png"
        )


def surface_from_animation(animation: Animation) -> pygame.surface.Surface:
    return animation.frames[animation.state][animation.frame_idx]
