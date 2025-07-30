from ..drawer import DrawerFast, Plane

from ..mixins import CallbackMixin, DepthMixin

from ..callbacks import ( OnUpdateContext, OnDrawContext, OnResizeContext, OnMoveContext,
                         OnKeyboardInputContext, OnFocusAddedContext, OnFocusLostContext )
from ..callbacks.widgets import OnInitContext

from ..datatypes import Size, Position, Point

class Widget(CallbackMixin, DepthMixin):
    def __init__(self, size: Size | tuple[int, int], position: Position | tuple[int, int], name: str = None):

        if not isinstance(size, (Size, tuple)):
            raise TypeError(
                f"Expected size to be of type `datatypes.Size` or `tuple[int, int]` but got {type(size)}."
            )
        if isinstance(size, tuple):
            size = Size(*size)

        self.size = size

        if not isinstance(position, (Position, tuple)):
            raise TypeError(
                f"Expected position to be of type `datatypes.Poition` or `tuple[int, int]` but got {type(position)}."
            )
        if isinstance(position, tuple):
            position = Position(*position)

        self.position = position
        
        self.name = name or self.__class__.__name__
        self.tick = -1
        
        # holds all callbacks based on their ids
        super().__init__([
            "on_draw",
            "on_move",
            "on_init",
            "on_update",
            "on_keyboard_input",
        ])
        self.add_callback("on_draw", self.on_draw)
        self.add_callback("on_move", self.on_move)
        
        self._run_callbacks(OnInitContext())

    def get_name(self):
        return self.name

    def should_get_focus(self, *args, **kwargs):
        return False
    
    def is_in_focus(self):
        return False

    def draw(self) -> Plane:
        drawer = DrawerFast(
            self.size.width,
            height=self.size.height,
        )
        self._run_callbacks(OnDrawContext(drawer))
        return drawer.get_plane()

    def on_draw(self, context = OnDrawContext):
        pass
    
    def move(self, position: Position = None):
        if position is None:
            return
        self.position = position
        self._run_callbacks(OnMoveContext(position=self.position))
    
    def on_move(self, context = OnMoveContext):
        pass

    def update(self, context: OnUpdateContext):
        tick = context.get_tick()
        if tick is not None:
            self.tick = tick
        self._run_callbacks(context)
        key = context.get_key()
        if (not context.is_cancelled()) and key is not None:
            on_keyboard_input_context = OnKeyboardInputContext(key)
            self._run_callbacks(on_keyboard_input_context)
            if on_keyboard_input_context.is_cancelled():
                context.cancel()
        

class InteractionWidget(Widget):
    def __init__(self, size: Size | tuple[int, int], position: Position | tuple[int, int], **kwargs):
        super().__init__(size, position, **kwargs)

        self.focused = False
        
        # extend callbacks
        super(Widget, self)._init_callbacks([
            "on_focus_added",
            "on_focus_lost",
        ])

    def should_get_focus(self, *args, **kwargs):
        return True
    
    def is_in_focus(self):
        return self.focused

    def unfocus(self):
        self.focused = False
        self._run_callbacks(OnFocusLostContext())

    def focus(self):
        self.focused = True
        self._run_callbacks(OnFocusAddedContext())

    # calculates the center point of this widget, used internally
    # for arrow key interactions
    def _get_center_point(self) -> Point:
        return Point(
            self.position.x + (self.size.width / 2),
            self.position.y + (self.size.height / 2)
        )
    
    # calculates the corners points of this widget, used internally
    # for arrow key interactions
    def _get_bouding_box(self) -> list[Point]:
        return [
            Point(self.position.x, self.position.y),
            Point(self.position.x + self.size.width, self.position.y),
            Point(self.position.x + self.size.width, self.position.y + self.size.height),
            Point(self.position.x, self.position.y + self.size.height),
        ]