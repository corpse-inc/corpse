import pygame
import esper

from dataclasses import dataclass as component


@component
class Size:
    w: float
    h: float
