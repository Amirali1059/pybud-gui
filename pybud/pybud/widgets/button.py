from types import FunctionType

from readchar import key as KeyPress

from .widget import InteractionWidget, Widget

from ..drawer import ansi
from ..datatypes import Size, Position
from ..callbacks import OnKeyboardInputContext, OnDrawContext
from ..callbacks.widgets.button import OnButtonPress

class Button(InteractionWidget):
    def __init__(
        self,
        text: str,
        size: Size | tuple[int, int] = (100, 10),
        position: Position | tuple[int, int] = (0, 0),
        **kwargs
    ):
        super().__init__(size, position, **kwargs)
        self.text = text
        self.size.height = 1

        super(Widget, self)._init_callbacks([
            "on_button_press"
        ])
        
        self.add_callback("on_keyboard_input", self._on_keyboard_input)
        self.add_callback("on_button_press", self.on_button_press)

    def _on_keyboard_input(self, context: OnKeyboardInputContext):
        if context.key == KeyPress.ENTER:
            self._run_callbacks(OnButtonPress())
            context.cancel()
    
    def on_button_press(self, context: OnButtonPress):
        pass

    def set_callback(self, func: FunctionType):
        return self.add_callback("on_button_press", func)
        
    def on_draw(self, context: OnDrawContext):
        drawer = context.drawer
        
        if self.is_in_focus():
            _option = ansi.AnsiString(
                self.text,
                #back = (round(drawer.plane_color[0] * 0.7), round(drawer.plane_color[1] * 0.7), drawer.plane_color[2]) if drawer.plane_color else None
            )
            _option.add_graphics(ansi.AnsiGraphicMode.BOLD | ansi.AnsiGraphicMode.UNDERLINE)
            drawer.text_colored_centered(
                text = _option,
                posy = 0,
            )
        else:
            _option = ansi.AnsiString(
                self.text,
                #back = tuple(map(lambda x: round(x * 0.6), drawer.plane_color)) if drawer.plane_color else None
            )
            drawer.text_colored_centered(
                text = _option,
                posy = 0,
            )