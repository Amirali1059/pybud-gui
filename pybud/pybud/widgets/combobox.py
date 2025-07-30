from types import FunctionType

from readchar import key as KeyPress

from .widget import InteractionWidget, Widget

from ..drawer import ansi
from ..datatypes import Size, Position
from ..callbacks import OnKeyboardInputContext, OnDrawContext
from ..callbacks.widgets.combobox import OnSelectionChanged

class ComboBox(InteractionWidget):
    def __init__(
        self,
        text: str | ansi.AnsiString,
        options: dict[str, FunctionType],
        default_option: int = 0,
        size: Size | tuple[int, int] = (100, 10),
        position: Position | tuple[int, int] = (0, 0),
        **kwargs
    ):
        super().__init__(size, position, **kwargs)
        if isinstance(text, str):
            text = ansi.AnsiString(text, fore=(220, 220, 220))
        self.text = text
        self.options = options.keys()
        self.n_options = len(self.options)
        if self.n_options == 0:
            raise ValueError("Expected `options` to have at least 1 item, but got nothing.")
        self.option_callbacks = list(options.values())
        self.selected_option_id = default_option
        self.size.height = 1

        super(Widget, self)._init_callbacks([
            "on_selection_changed"
        ])
        
        self.add_callback("on_keyboard_input", self._on_keyboard_input)

    def _on_keyboard_input(self, context: OnKeyboardInputContext):
        match context.key:
            case KeyPress.ENTER:
                self.option_callbacks[self.selected_option_id]()
                context.cancel()
            case KeyPress.UP:
                self.selected_option_id = (self.selected_option_id - 1) % self.n_options
                self._run_callbacks(OnSelectionChanged(self.selected_option_id))
                context.cancel()
            case KeyPress.DOWN:
                self.selected_option_id = (self.selected_option_id + 1) % self.n_options
                self._run_callbacks(OnSelectionChanged(self.selected_option_id))
                context.cancel()

    def on_draw(self, context: OnDrawContext):
        drawer = context.drawer
        
        drawer.text_colored(text = self.text, posx = 0, posy = 0)
        
        # this is intended to be a for loob because sometimes self.selected_option_id doesn't
        # match any index of the options list and therefore no option is selected
        for i, option in enumerate(self.options):
            if i == self.selected_option_id:
                _option = ansi.AnsiString(
                    f" {option} ".ljust(self.size.width - len(self.text)),
                    #back = tuple(map(lambda x: round(x * 0.8), drawer.plane_color)) if drawer.plane_color else None
                )
                _option.add_graphics(ansi.AnsiGraphicMode.UNDERLINE)
                drawer.text_colored(
                    text = _option,
                    posx = len(self.text),
                    posy = 0
                )