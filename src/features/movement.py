from dataclasses import dataclass as component


@component
class Movement:
    x: float = 0.0
    y: float = 0.0


@component
class Velocity:
    x: float = 0.0
    y: float = 0.0
