import pygame


def snake_to_camel_case(snake_case_string: str) -> str:
    return "".join(c.title() for c in snake_case_string.split("_"))


def animation_from_surface(surface: pygame.surface.Surface):
    from animation import Animation

    return Animation(frames=(surface,))


def surface_from_animation(animation) -> pygame.surface.Surface:
    return animation.frames[animation._frame]
