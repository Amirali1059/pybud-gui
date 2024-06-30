from .color import ColorMode, AnsiColor

class AnsiGraphicMode:
    BOLD: AnsiGraphics
    FAINT: AnsiGraphics
    ITALIC:AnsiGraphics
    UNDERLINE:AnsiGraphics
    BLINKING:AnsiGraphics
    REVERSE:AnsiGraphics
    HIDDEN:AnsiGraphics
    STRIKE:AnsiGraphics

def init() -> None: ...

class AnsiGraphics:
    mode: int
    def __init__(self) -> None: ...
    @staticmethod
    def to_string(reset: bool) -> str: ...
    def __str__(self) -> str: ...
    def __eq__(self, other: 'AnsiGraphics') -> bool: ...


class AnsiChar:
    char: str
    back_color: AnsiColor
    fore_color: AnsiColor
    graphics: AnsiGraphics
    def __init__(self, char: str, fore: tuple[int, int, int] = None, back: tuple[int, int, int] = None) -> None: ...
    def to_string(self, mode: ColorMode) -> str: ...
    def __str__(self) -> str: ...
    def set(self, c: str) -> None: ...
    def as_ansistring(self) -> AnsiString: ...
    def __add__(self, other: 'AnsiChar') -> AnsiString: ...

class AnsiString:
    vec: list[AnsiChar]
    def __init__(self, str: str, fore: tuple[int, int, int] = None, back: tuple[int, int, int] = None) -> None: ...
    def to_string(self, mode: ColorMode) -> str: ...
    def split_at(self, mid: int) -> tuple[AnsiString, AnsiString]: ...
    def place(self, text: AnsiString, pos: int, assign: bool)  -> None: ...
    def place_str(self, text: str, pos: int)  -> None: ...
    def center_place(self, text: AnsiString, assign: bool)  -> None: ...
    def center_place_str(self, text: str)  -> None: ...
    def add_graphics(self, agm: AnsiGraphics) -> None: ...
    def __add__(self, other: 'AnsiString') -> 'AnsiString': ...
    def __len__(self) -> int: ...
    def __str__(self) -> str: ...