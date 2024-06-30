import os
from pybud._drawer import ansi

AnsiGraphics = ansi.AnsiGraphics
AnsiChar = ansi.AnsiChar
AnsiString = ansi.AnsiString

# this ugly, but we can't do nothing about it
class AnsiGraphicMode:
    BOLD = AnsiGraphics._from_bits(0b00000001)
    FAINT = AnsiGraphics._from_bits(0b00000010)
    ITALIC = AnsiGraphics._from_bits(0b00000100)
    UNDERLINE = AnsiGraphics._from_bits(0b00001000)
    BLINKING = AnsiGraphics._from_bits(0b00010000)
    REVERSE = AnsiGraphics._from_bits(0b00100000)
    HIDDEN = AnsiGraphics._from_bits(0b01000000)
    STRIKE = AnsiGraphics._from_bits(0b10000000)

def init():
    """only for windows"""
    os.system("")