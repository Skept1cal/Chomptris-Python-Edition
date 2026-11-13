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
'''
CHARS: list[list[int] | None] = [None for _ in range(128)]

CHARS[ord(' ')] = [
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
]
CHARS[ord('!')] = [
    0b0110,
    0b0110,
    0b0110,
    0b0110,
    0b0000,
    0b0000,
    0b0110,
    0b0110,
]
CHARS[ord('"')] = [
    0b1001,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
]
CHARS[ord('#')] = [
    0b0110,
    0b0110,
    0b1111,
    0b0110,
    0b0110,
    0b1111,
    0b0110,
    0b0110,
]
CHARS[ord('$')] = [
    0b0000,
    0b0110,
    0b1111,
    0b1100,
    0b0110,
    0b0011,
    0b1111,
    0b0110,
]
CHARS[ord('%')] = [
    0b1101,
    0b1101,
    0b0010,
    0b0010,
    0b0100,
    0b0100,
    0b1011,
    0b1011,
]
CHARS[ord('&')] = [
    0b0000,
    0b1110,
    0b1000,
    0b1000,
    0b1111,
    0b1010,
    0b1010,
    0b1110,
]
CHARS[ord('\'')] = [
    0b0100,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
]
CHARS[ord('(')] = [
    0b0011,
    0b0110,
    0b0110,
    0b1100,
    0b1100,
    0b0110,
    0b0110,
    0b0011,
]
CHARS[ord(')')] = [
    0b1100,
    0b0110,
    0b0110,
    0b0011,
    0b0011,
    0b0110,
    0b0110,
    0b1100,
]
CHARS[ord('*')] = [
    0b0110,
    0b0110,
    0b1111,
    0b0110,
    0b1001,
    0b0000,
    0b0000,
    0b0000,
]
CHARS[ord('+')] = [
    0b0000,
    0b0110,
    0b0110,
    0b1111,
    0b1111,
    0b0110,
    0b0110,
    0b0000,
]
CHARS[ord(',')] = [
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0110,
    0b0110,
    0b1100,
]
CHARS[ord('-')] = [
    0b0000,
    0b0000,
    0b0000,
    0b1111,
    0b1111,
    0b0000,
    0b0000,
    0b0000,
]
CHARS[ord('.')] = [
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0000,
    0b0110,
    0b0110,
]
CHARS[ord('/')] = [
    0b0001,
    0b0001,
    0b0010,
    0b0110,
    0b0100,
    0b1000,
    0b1000,
]
CHARS[ord('0')] = [
    0b0110,
    0b1001,
    0b1011,
    0b1111,
    0b1101,
    0b1001,
    0b1001,
    0b0110,
]
CHARS[ord('1')] = [
    0b0110,
    0b1110,
    0b0110,
    0b0110,
    0b0110,
    0b0110,
    0b0110,
    0b1111,
]
CHARS[ord('2')] = [
    0b0110,
    0b1001,
    0b0010,
    0b0010,
    0b0110,
    0b0100,
    0b0100,
    0b1111,
]
CHARS[ord('3')] = [
    0b0110,
    0b1001,
    0b0001,
    0b1110,
    0b0001,
    0b1001,
    0b0110,
]
'''