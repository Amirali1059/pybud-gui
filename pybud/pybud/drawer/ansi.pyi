from .color import ColorMode

class AnsiGraphicMode: 
    Bold      = 0,
    Faint     = 1,
    Italic    = 2,
    Underline = 3,
    Blinking  = 4,
#   Undefined = 5,
    Reverse   = 6,
    Hidden    = 7,
    Strike    = 8,
    ...


class AnsiGraphics:
    modes: list = ...

    def __init__(self) -> None: ...
    @staticmethod
    def get_mode(mode: AnsiGraphicMode, reset: bool) -> str: ...
    def to_string(reset: bool) -> str: ...
    def __str__(self) -> str: ...
    def is_eq(self, other: 'AnsiGraphics') -> bool: ...
    def add(self, agm: AnsiGraphicMode) -> None: ...
    def __add__(self, agm: 'AnsiGraphicMode') -> 'AnsiGraphics': ...


class AnsiChar:
    def __init__(self, char: str, fore: tuple[int, int, int] = None, back: tuple[int, int, int] = None) -> None: ...
    def __str__(self) -> str: ...
    def __add__(self, other: 'AnsiChar') -> 'AnsiString': ...
    def setchar(self, c: str) -> None: ...
    def as_ansistring(self) -> AnsiString: ...

class AnsiString:
    def __init__(self, str: str, fore: tuple[int, int, int] = None, back: tuple[int, int, int] = None) -> None: ...
    def __add__(self, other: 'AnsiString') -> 'AnsiString': ...
    def __str__(self) -> str: ...
    def to_string(self, mode: ColorMode) -> str: ...
    def split_at(self, mid: int) -> tuple[AnsiString, AnsiString]: ...
    def place(self, text: AnsiString, pos: int, assign: bool)  -> None: ...
    def place_str(self, text: str, pos: int)  -> None: ...
    def center_place(self, text: AnsiString, assign: bool)  -> None: ...
    def center_place_str(self, text: str)  -> None: ...
    def add_graphics(self, agm: AnsiGraphicMode) -> None: ...