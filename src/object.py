from dataclasses import dataclass as component

@component
class Size:
    w: float
    h: float


@component
class Solid:
    pass


@component
class Invisible:
    pass
