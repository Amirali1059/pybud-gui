from readchar import key as KeyPress

from .callbacks import OnKeyboardInputContext, OnUpdateContext, OnDrawContext, OnMoveContext, OnResizeContext, OnFocusAddedContext, OnFocusLostContext
from .callbacks.window import OnOpenContext, OnCloseContext
from .drawer import DrawerFast, Plane
from .datatypes import Size, Position
from .datatypes.color import Color
from .enums import WindowClosingReason
from .mixins import CallbackMixin, DepthMixin
from .mixins.callbackmixin import CallbackResult
from .widgets import Widget, InteractionWidget


def exists(v):
    CallbackResult
    return v is not None


class Window(CallbackMixin, DepthMixin):
    """
    A `Window` is the main display plane in witch all the widgets will be drawn to, 
    it has a size and position and must be passed to a `Session` to be handled properly.
    """

    def __init__(
        self,
        size: Size | tuple[int, int],
        position: Position | tuple[int, int],
        title: str | None = None,
        has_border: bool = True,
        background: Color | tuple[int, int, int] | None = None,
    ):
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
        
        if background:
            if not isinstance(background, (Color, tuple)):
                raise TypeError(
                    f"Expected background to be of type `datatypes.Color` or `tuple[int, int, int]` but got {type(background)}."
                )
            if isinstance(background, tuple):
                background = Color(*background)
        
            self.background = background
        else:
            self.background = None

        self.title = title or self.__class__.__name__
        self.has_border = has_border

        self.is_open = False
        self.is_in_focus = False

        self._widgets: list[Widget] = []
        self._focus_widget: Widget = None

        self.tick = 0

        # holds all callbacks based on their ids
        super().__init__([
            "on_draw",
            "on_open",
            "on_close",
            "on_focus_added",
            "on_focus_lost",
            "on_resize",
            "on_move",
            "on_update",
            "on_keyboard_input"
        ])

        self.add_callback("on_resize", self.on_resize)

    def unfocus(self):
        self.is_in_focus = False
        self._run_callbacks(OnFocusLostContext())

    def focus(self):
        self.is_in_focus = True
        self._run_callbacks(OnFocusAddedContext())

    def _trace_closest_widget(self, origin: InteractionWidget, mode: int, delta: float = 1.0) -> Widget | None:
        corner_points = origin._get_bouding_box()
        o_point = origin._get_center_point()

        match mode:
            case 0:  # UP
                # corners to be used for the calculations
                c0 = corner_points[0]
                c1 = corner_points[1]
                # the weights of x and y axis diffrence
                x_w = 1.0
                y_w = -delta
            case 1:  # RIGHT
                c0 = corner_points[1]
                c1 = corner_points[2]
                x_w = -delta
                y_w = 1.0
            case 2:  # DOWN
                c0 = corner_points[2]
                c1 = corner_points[3]
                x_w = 1.0
                y_w = -delta
            case 3:  # LEFT
                c0 = corner_points[3]
                c1 = corner_points[0]
                x_w = -delta
                y_w = 1.0
            case _:
                raise ValueError(f"Invalid mode: {mode}")

        applicable_widgets = []
        for w in reversed(self._widgets):
            if w is origin or not isinstance(w, InteractionWidget):
                continue

            w_point = w._get_center_point()

            d_x0 = abs(w_point.x - c0.x)
            d_x1 = abs(w_point.x - c1.x)
            d_x = (d_x0 + d_x1) * x_w * 0.5

            d_y0 = w_point.y - c0.y
            d_y1 = w_point.y - c1.y
            d_y = (d_y0 + d_y1) * y_w

            delta_score = d_x + d_y

            delta_threshhold = abs(c0.x - c1.x) + abs(c0.y - c1.y)

            # Check if the widget is in the direction of the mode
            if delta_score <= delta_threshhold:
                applicable_widgets.append((w, w_point))

        # find the widget were its center point is the closest to the origin point
        min_distance = float("inf")
        chosen_widget = None
        for w, w_point in applicable_widgets:
            w_distance = o_point.distance_to(w_point)
            if w_distance < min_distance:
                min_distance = w_distance
                chosen_widget = w
        return chosen_widget

    def resize(self, size: Size = None):
        if size is None:
            return
        self.size = size
        self._run_callbacks(OnResizeContext(self.size))

    def on_resize(self):
        pass

    def update(self, context: OnUpdateContext):
        if exists(context.tick):
            self.tick = context.tick
        self._run_callbacks(context)
        if context.key is not None:
            self._run_callbacks(OnKeyboardInputContext(context.key))
        if exists(self._focus_widget):
            self._focus_widget.update(context)
        if context.is_cancelled():
            return
        match context.key:
            case KeyPress.CTRL_C:
                self.close(WindowClosingReason.KeyboardInterrupt)
                context.cancel()
            case KeyPress.TAB:
                chosen_widget = None
                for w in self._widgets:
                    if w is self._focus_widget or not isinstance(w, InteractionWidget):
                        continue
                    chosen_widget = w
                    break
                if chosen_widget:
                    self.set_focus_widget(chosen_widget)
                    context.cancel()
            case KeyPress.UP:
                if self._focus_widget is not None:
                    chosen_widget = self._trace_closest_widget(
                        origin=self._focus_widget,
                        mode=0,
                    )
                    if chosen_widget:
                        self.set_focus_widget(chosen_widget)
                        context.cancel()
            case KeyPress.DOWN:
                if self._focus_widget is not None:
                    chosen_widget = self._trace_closest_widget(
                        origin=self._focus_widget,
                        mode=2,
                    )
                    if chosen_widget:
                        self.set_focus_widget(chosen_widget)
                        context.cancel()
            case KeyPress.RIGHT:
                if self._focus_widget is not None:
                    chosen_widget = self._trace_closest_widget(
                        origin=self._focus_widget,
                        mode=1,
                    )
                    if chosen_widget:
                        self.set_focus_widget(chosen_widget)
                        context.cancel()
            case KeyPress.LEFT:
                if self._focus_widget is not None:
                    chosen_widget = self._trace_closest_widget(
                        origin=self._focus_widget,
                        mode=3,
                    )
                    if chosen_widget:
                        self.set_focus_widget(chosen_widget)
                        context.cancel()

    def set_focus_widget(self, chosen_widget):
        self._widgets.remove(chosen_widget)
        self._widgets.append(chosen_widget)
        self._update_widget_focus()

    def add_widget(self, widget: Widget):
        widget._set_depth(max([0]+[w._get_depth() for w in self._widgets])+1)
        self._widgets.append(widget)
        self._update_widget_focus()

    def bring_widget_to_front(self, widget: Widget):
        # TODO: Don't update unnecessary widgets
        for w in self._widgets:
            if w is widget:
                w._set_depth(0)
            else:
                w._set_depth(1+w._get_depth())

    # sets the last widget in `self._widgets` to be in focus and others to not be in focus
    def _update_widget_focus(self):
        focus_granted = False
        for w in reversed(self._widgets):
            if isinstance(w, InteractionWidget):
                if w.should_get_focus() and not focus_granted:
                    w.focus()
                    self._focus_widget = w
                    focus_granted = True
                else:
                    w.unfocus()
        if not focus_granted:
            self._focus_widget = None

    def draw(self) -> Plane:
        if not self.is_open:
            return

        # create a new instance of drawer for this window
        drawer = DrawerFast(
            width=self.size.width,
            height=self.size.height,
            plane_color=self.background,
        )
        
        drawer.text(f"[ {self.title} ]", posx=1, posy=0)

        # draw widgets in order of depth acending
        for w in sorted(self._widgets, key=lambda x: x._get_depth()):
            drawer.place_plane(
                plane=w.draw(),
                posx=w.position.x,
                posy=w.position.y
            )
        # run window's draw callbacks
        self._run_callbacks(OnDrawContext(drawer))
        
        return drawer.get_plane()

    def open(self):
        self.is_open = True
        self._run_callbacks(OnOpenContext())

    def close(self, reason: int):
        self.is_open = False
        self._run_callbacks(OnCloseContext(reason))
