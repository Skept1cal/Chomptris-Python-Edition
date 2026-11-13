from typing import Literal
import pygame
from constants import *
from defs import Pos

def renderFont(screen: pygame.Surface, text: str, pos: Pos, invert: bool):
    bgInd = 0 if (not invert) else 1
    fgInd = int(not bgInd)
    surface: pygame.Surface = FONT.render(
        text,               # text
        True,               # antialias
        TEXT_COLORS[fgInd], # color
        TEXT_COLORS[bgInd]  # background
    )
    screen.blit(
        source = surface,
        dest   = (pos.x, pos.y)
    )