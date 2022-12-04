from dataclasses import dataclass as component

import esper

from render import Renderable


@component
class Size:
    w: float
    h: float


@component
class Solid:
    pass


@component
class MakeInvisibleRequest:
    pass


@component
class Invisible:
    pass
