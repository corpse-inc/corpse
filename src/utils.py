from pyscroll.data import pygame
from animation import Animation, AnimationState


FPS = 60

RESOLUTION = 320, 320
CAMERA_SIZE = RESOLUTION

# TODO: Баг: при изменении данной константы система rotation.RotationProcessor
# неправильно вращает спрайты.
CAMERA_ZOOM = 1

PLAYER_SPEED = 3

RESOURCES = "/".join(__file__.split("/")[:-2]) + "/resources"


class ResourcePath:
    @classmethod
    def location_tilemap(cls, location_id: str) -> str:
        return f"{RESOURCES}/locations/tilemaps/{location_id}/tilemap.tmx"

    @classmethod
    def creature_frame(cls, creature: str, state: AnimationState, idx: int) -> str:
        return f"{RESOURCES}/creatures/{creature}/{state.name}/{idx}.png"


def surface_from_animation(animation: Animation) -> pygame.surface.Surface:
    return animation.frames[animation.state][animation.frame_idx]
