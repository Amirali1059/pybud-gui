from readchar import key as Key

from .widget import InteractionWidget

from ..drawer import ansi
from ..datatypes import Size, Position
from ..callbacks import OnDrawContext, OnKeyboardInputContext


class TextBox(InteractionWidget):
    def __init__(
        self,
        text: str,
        allowed_chars: str = None,
        size: Size | tuple[int, int] = (100, 10),
        position: Position | tuple[int, int] = (0, 0),
        **kwargs
    ):
        super().__init__(size, position, **kwargs)
        # p = 1
        self.size.height = 1
        self.text = text
        self.height = 1
        self.input = ""
        self.pointer = 0
        self.view = 0

        # characters that this widget will listen to
        self.allowed_characters = allowed_chars or ""

        self.__ignored_keys = self._initialize_ignored_keys()

        self.add_callback("on_keyboard_input", self._on_keyboard_input)

    def _initialize_ignored_keys(self):
        ctrl_keys = [getattr(Key, f"CTRL_{chr(i)}") for i in range(ord('A'), ord('Z') + 1)]
        function_keys = [getattr(Key, f"F{i}") for i in range(1, 13)]
        command_keys = [
            Key.DOWN, Key.UP, Key.LEFT, Key.RIGHT, Key.END, Key.HOME, Key.ESC, Key.ENTER,
            Key.INSERT, Key.LF, Key.CR, Key.PAGE_DOWN, Key.PAGE_UP, Key.SUPR, Key.BACKSPACE
        ]
        return ctrl_keys + function_keys + command_keys

    def reset(self):
        self.input = ""
        self.pointer = 0
        self.view = 0

    def get_max_length(self):
        return self.size.width - len(self.text) - 2

    def _on_keyboard_input(self, context: OnKeyboardInputContext):
        key = context.key

        max_input_len = self.get_max_length()

        # capture and place characters
        if key not in self.__ignored_keys:
            self.input = self.input[:self.pointer] + key + self.input[self.pointer:]
            self.pointer += 1
            if (len(self.input)-self.view) > (max_input_len-1):
                self.view += 1
            return

        match key:
            case Key.BACKSPACE:
                if self.pointer != 0:
                    self.input = self.input[:self.pointer-1] + self.input[self.pointer:]
                else:
                    self.input = self.input[self.pointer:]
                self.pointer = max(self.pointer-1, 0)
                if self.pointer-self.view < 0:
                    self.view = max(self.view - max_input_len, 0)
                context.cancel()

            case Key.DELETE:
                self.input = self.input[:self.pointer] + self.input[self.pointer+1:]
                # self.pointer = max(self.pointer - 1, 0)
                context.cancel()

            case Key.LEFT:
                self.pointer = max(self.pointer - 1, 0)
                if self.pointer-self.view < 0:
                    self.view = max(self.view - 1, 0)
                context.cancel()

            case Key.RIGHT:
                self.pointer = min(self.pointer + 1, len(self.input))
                if self.view == (self.pointer-max_input_len):
                    self.view = min(self.view + 1, len(self.input))
                context.cancel()

    def format_textbox(self):
        text, inp, pointer, view = self.text, self.input, self.pointer, self.view
        max_input_len = self.get_max_length()
        # get the input text with fixed length plus one extra space for the pointer
        if view+max_input_len-1 < len(inp):
            inp_ = inp[view:view+max_input_len]
        else:
            inp_ = inp[view:view+max_input_len-1] + " "

        pointer_str = ansi.AnsiString(inp_[pointer-view])
        show_pointer = (self.tick % 20) >= 12

        if self.focused and show_pointer or inp_[pointer-view] != " ":
            pointer_str.add_graphics(ansi.AnsiGraphicMode.REVERSE)

        # insert the pointer into input text at the correct position
        input_plus_pointer = ansi.AnsiString(inp_[:pointer-view]) + pointer_str + ansi.AnsiString(inp_[pointer-view+1:])

        if isinstance(text, str):
            title = ansi.AnsiString(text, fore=(220, 220, 220))
        elif isinstance(text, ansi.AnsiString):
            title = text
        fstr = ansi.AnsiString("")
        back_exists = ansi.AnsiString("<", fore=(50, 200, 50))
        forward_exists = ansi.AnsiString(">", fore=(50, 200, 50))

        fstr = fstr + (back_exists if view != 0 else ansi.AnsiString(" "))
        fstr = fstr + input_plus_pointer + ansi.AnsiString(" " * (max_input_len - len(input_plus_pointer)))
        fstr = fstr + (forward_exists if view+max_input_len-1 < len(inp) else ansi.AnsiString(" "))

        fstr.add_graphics(ansi.AnsiGraphicMode.UNDERLINE)
        return title + fstr

    def on_draw(self, context: OnDrawContext):
        drawer = context.drawer
        # TODO: check if there is a background, if so, draw a shadow for the textbox to be indicated
        #if drawer.plane_color is not None:
        #    text_shadow = tuple(map(lambda x: round(x * 0.8), list(drawer.plane_color)))
        #    drawer.text_colored(
        #        text=ansi.AnsiString(" " * (self.size.width - len(self.text)), back=text_shadow),
        #        posx=len(self.text),
        #        posy=0,
        #    )
        drawer.text_colored(
            text=self.format_textbox(),
            posx=0,
            posy=0,
        )
