DEFAULT_BACKGROUND_COLOR = None  # (90, 90, 255)


class Point:
    def __init__(self, x: int = 0, y: int = 0) -> None:
        assert x >= 0
        assert y >= 0
        self.x = x
        self.y = y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def distance_squared(self, other):
        if isinstance(other, Point):
            return (self.x - other.x) ** 2 + (self.y - other.y) ** 2
        elif isinstance(other, tuple) or isinstance(other, list):
            return (self.x - other[0]) ** 2 + (self.y - other[1]) ** 2
        else:
            raise NotImplementedError()

    def distance(self, other):
        return self.distance_squared(other) ** 0.5

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        elif isinstance(other, tuple) or isinstance(other, list):
            return Point(self.x + other[0], self.y + other[1])
        else:
            raise NotImplementedError()

    def __iadd__(self, p2: 'Point'):
        return self + p2


class Size:
    def __init__(self, w: int = 0, h: int = 0) -> None:
        assert w >= 0
        assert h >= 0
        self.w = w
        self.h = h

    def getWidth(self) -> int:
        return self.w

    def getHeight(self) -> int:
        return self.h

    def getArea(self):
        return self.getWidth() * self.getHeight()

    def __add__(self, other):
        if isinstance(other, Size):
            return Point(self.getWidth() + other.getWidth(), self.getHeight() + other.getHeight())
        elif isinstance(other, tuple) or isinstance(other, list):
            return Point(self.getWidth() + other[0], self.getHeight() + other[1])
        else:
            raise NotImplementedError()

    def __iadd__(self, other):
        return self + other
