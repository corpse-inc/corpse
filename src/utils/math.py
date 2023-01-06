import math
import pygame


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


def vector_angle(vector: pygame.Vector2) -> float:
    return vector.as_polar()[1]
