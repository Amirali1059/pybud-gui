class ColorMode:
    LIMITED = ...
    TRUECOLOR = ...

class ColorGround:
    BACK = ...
    FORE = ...

class AnsiColor:
    def __init__(self, r: int, g: int, b: int) -> None: ...
    def to_string(self, mode: ColorMode, ground: ColorGround) -> str: ...
    def __eq__(self, other: object) -> bool: ...