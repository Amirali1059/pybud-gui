
import types

from pybud.drawer import Drawer
from pybud.drawer.ansi import AnsiGraphicMode
from pybud.drawer.ansi import AnsiString as AStr
from pybud.drawer.color import ColorMode

from readchar import key as Key

def default(d: dict, k:str, default):
    if k in d.keys():
        return d[k]
    else:
        return default

class WidgetBase():
    def __init__(self, size: list[int, int] = None, pos: list[int, int] = [0, 0], **kwargs):
        # set variabled
        self.ctype = default(kwargs, "ctype", ColorMode.LIMITED)
        self.size = [6, 60] if size is None else size
        self.pos = [0, 0] if pos is None else pos
        # defaults
        self.background_color = None
        self.name = default(kwargs, "name", "__name__")
        self.parent = None
        self.is_selected = False
        self.selectable = False
        
        # holds all callbacks
        self._callbacks = {
            "on_parent_change": [],
            "on_add": [],
            "on_render": [],
            "on_interrupt": [],
            "on_enter": [],
            "on_update": [],
        }

    def add_callback(self, calllback_id: str, fn):
        assert calllback_id in self._callbacks.keys(), f"callback_id=\"{calllback_id}\" does not exist, available options: {list(self._callbacks.keys())}"
        self._callbacks[calllback_id].append(fn)

    def _run_callback(self, calllback_id: str, **kwargs):
        assert calllback_id in self._callbacks.keys(), f"callback_id=\"{calllback_id}\" does not exist, available options: {list(self._callbacks.keys())}"
        return [fn(**kwargs) for fn in self._callbacks[calllback_id]]

    def get_name(self):
        name = self.__class__.__name__
        c = 0
        for w in self.parent.widgets:
            if isinstance(w, self.__class__):
                c += 1
        return name + "_" + str(c+1)

    def on_add(self, parent):
        self._run_callback("on_add", parent = parent)
        if self.parent == parent: return
        self.parent = parent
        if self.name == "__name__":
            self.name = self.get_name()
        self._run_callback("on_parent_change")

    def on_interrupt(self):
        self._run_callback("on_interrupt")

    def render(self):
        drawer = Drawer(size=tuple(self.size[::-1]), plane_color=self.background_color)
        self._run_callback("on_render", drawer = drawer)
        return drawer

    def update(self, key):
        self._run_callback("on_update", key = key)
        if key == Key.ENTER:
            self._run_callback("on_enter")
        return key

class InteractableWidget(WidgetBase):
    def __init__(self, size: list[int, int] = None, pos: list[int, int] = [0, 0], **kwargs):
        super().__init__(size, pos, **kwargs)
        # defaults
        self.is_disabled = False
        self.selectable = True
        self.result = None

    def on_interrupt(self):
        super().on_interrupt()
        self.is_disabled = True

class WidgetLabel(WidgetBase):
    def __init__(self,
                 text,
                 centered: bool = True,
                 wordwrap: bool = True,
                 size: list[int, int] = None,
                 pos: list[int, int] = [0, 0],
                 padding: int = 2,
                 **kwargs
                 ):

        super().__init__(size, pos, **kwargs)

        if isinstance(text, str):
            self.text = AStr(text, fore = (220, 220, 220))
        elif isinstance(text, AStr):
            self.text = text
        else:
            raise NotImplementedError()

        self.pad = padding
        self.size[1] = (len(text) // (self.size[0] - (2*self.pad))) + 1
        self.centered = centered
        self.wordwrap = wordwrap

        self.add_callback("on_render", self.on_render)

    def place_text(self, drawer, text, ln_idx):
        def _place_text(t, ypos):
            if self.centered:
                drawer.center_place(t, ypos = ypos, assign = False)
            else:
                drawer.place(t, pos=(ypos, 0), assign = False)

        p = 2*self.pad

        if len(text) > (self.size[0] - p):
            for i in range(len(text)):
                i_ = len(text) - i - 1
                if i_ > (self.size[0] - p):
                    continue
                if isinstance(text, str) and text[i_] == " ":
                    _place_text(text[:i_], ln_idx)
                    return self.place_text(drawer, text[i_+1:], ln_idx + 1)
                if isinstance(text, AStr) and text.vec[i_].char == " ":
                    t_0, t_1 = text.split_at(i_)
                    _place_text(t_0, ln_idx)
                    return self.place_text(drawer, t_1, ln_idx + 1)
        else:
            _place_text(text, ln_idx)

    def on_render(self, drawer: Drawer):
        self.place_text(drawer, self.text, ln_idx = 0)


class WidgetOptions(InteractableWidget):
    def __init__(self,
                 options: list[tuple[str, types.FunctionType]],
                 text: str = "Options:",
                 default_option: int = 0,
                 size: list[int, int] = None,
                 pos: list[int, int] = [0, 0],
                 **kwargs
                 ):

        super().__init__(size, pos, **kwargs)
        self.n_options = len(options)
        self.options = list(map(lambda x: x[0], options))
        self.text = text
        self.callbacks = list(map(lambda x: x[1], options))
        self.selected = default_option
        self.size[1] = 1 + self.n_options

        self._callbacks.update({
            "on_keyboard_up": [],
            "on_keyboard_down": [],
        })

        self.add_callback("on_keyboard_up", self.on_keyboard_up)
        self.add_callback("on_keyboard_down", self.on_keyboard_down)

        self.add_callback("on_render", self.on_render)
        self.add_callback("on_enter", self.on_enter)

    def on_enter(self):
        self.result = self.callbacks[self.selected](self.parent)
        return self.result

    def on_keyboard_up(self):
        self.selected = (self.selected - 1) % self.n_options

    def on_keyboard_down(self):
        self.selected = (self.selected + 1) % self.n_options

    def update(self, key):
        key = super().update(key)
        if key == Key.UP:
            self._run_callback("on_keyboard_up")
            return
        if key == Key.DOWN:
            self._run_callback("on_keyboard_down")
            return
        return key

    def on_render(self, drawer: Drawer):
        caption_start = 2
        __options = self.text.ljust(self.size[0] - caption_start)
        drawer.place(AStr(__options, fore = (220, 220, 220)), pos = (0, caption_start), assign = False)
        for i, option in enumerate(self.options):
            if i == self.selected:
                option_color = (50, 220, 80)
                option_indicator = AStr("> ", fore=(220, 220, 220))
            else:
                option_color = (220, 220, 220)
                option_indicator = AStr("  ", fore=(220, 220, 220))
            __option = AStr(option, fore=option_color)
            drawer.place(option_indicator + __option, pos=(i + 1, caption_start), assign = False)


class WidgetInput(InteractableWidget):
    def __init__(self,
                 text: str,
                 size: list[int, int] = None,
                 pos: list[int, int] = [0, 0],
                 **kwargs
                 ):

        super().__init__(size, pos, **kwargs)
        # p = 1
        self.size[1] = 1
        self.text = text
        self.height = 1
        self.input = ""
        self.pointer = 0
        self.view = 0
        self.show_pointer = False

        # characters that this dialouge will listen to
        self.allowed_characters = default(kwargs, "allowed_chars", "")

        ## keys
        ctrl_keys = [
            Key.CTRL_A,
            Key.CTRL_B,
            Key.CTRL_C,
            Key.CTRL_D,
            Key.CTRL_E,
            Key.CTRL_F,
            Key.CTRL_G,
            Key.CTRL_H,
            Key.CTRL_I,
            Key.CTRL_J,
            Key.CTRL_K,
            Key.CTRL_L,
            Key.CTRL_M,
            Key.CTRL_N,
            Key.CTRL_O,
            Key.CTRL_P,
            Key.CTRL_Q,
            Key.CTRL_R,
            Key.CTRL_S,
            Key.CTRL_T,
            Key.CTRL_U,
            Key.CTRL_V,
            Key.CTRL_W,
            Key.CTRL_X,
            Key.CTRL_Y,
            Key.CTRL_Z,
        ]

        funcion_keys = [
            Key.F1,
            Key.F2,
            Key.F3,
            Key.F4,
            Key.F5,
            Key.F6,
            Key.F7,
            Key.F8,
            Key.F9,
            Key.F10,
            Key.F11,
            Key.F12,
        ]

        command_keys = [
            Key.DOWN,
            Key.UP,
            Key.LEFT,
            Key.RIGHT,
            Key.END,
            Key.HOME,
            Key.ESC,
            Key.ENTER,
            Key.INSERT,
            Key.LF,
            Key.CR,
            Key.PAGE_DOWN,
            Key.PAGE_UP,
            Key.SUPR,
            Key.BACKSPACE,
        ]

        self.__ignored_keys = ctrl_keys + funcion_keys + command_keys

        self.add_callback("on_render", self.on_render)
        self.add_callback("on_enter", self.on_enter)

    def on_enter(self):
        self.parent.close()
        self.result = self.input
        return self.result

    def reset(self):
        self.input = ""
        self.pointer = 0
        self.view = 0

    def get_max_length(self):
        p = 2
        max_input_len = self.size[0] - (p * 2)- len(self.text)
        return max_input_len

    def update(self, key):
        key = super().update(key)
        if key is None:
            return

        max_input_len = self.get_max_length()
        # capture and place characters
        if key != "UPDATE" and key not in self.__ignored_keys:
            self.input = self.input[:self.pointer] + \
                key + self.input[self.pointer:]
            self.pointer += 1
            if (len(self.input)-self.view) > (max_input_len-1):
                self.view += 1
            return

        # backspace
        if key == Key.BACKSPACE:
            if self.pointer != 0:
                self.input = self.input[:self.pointer-1] + self.input[self.pointer:]
            else:
                self.input = self.input[self.pointer:]
            self.pointer = max(self.pointer-1, 0)
            if self.pointer-self.view < 0:
                self.view = max(self.view - max_input_len, 0)
            return

        # delete
        if key == Key.DELETE:
            self.input = self.input[:self.pointer] + self.input[self.pointer+1:]
            # self.pointer = max(self.pointer - 1, 0)
            return

        # left arrow
        if key == Key.LEFT:
            self.pointer = max(self.pointer - 1, 0)
            if self.pointer-self.view < 0:
                self.view = max(self.view - 1, 0)
            return

        # right arrow
        if key == Key.RIGHT:
            self.pointer = min(self.pointer + 1, len(self.input))
            if self.view == (self.pointer-max_input_len):
                self.view = min(self.view + 1, len(self.input))
            return

        if key == "UPDATE":
            self.show_pointer = (self.parent.tick % 20) >= 12
        return key

    def format_textbox(self):
        text, inp, pointer, view = self.text, self.input, self.pointer, self.view
        max_input_len = self.get_max_length()
        # get the input text with fixed length plus one extra space for the pointer
        if view+max_input_len-1 < len(inp):
            inp_ = inp[view:view+max_input_len]
        else:
            inp_ = inp[view:view+max_input_len-1] + " "

        pointer_str = AStr(inp_[pointer-view])

        if not self.is_disabled and self.show_pointer or inp_[pointer-view] != " ":
            #pointer_str = AStr(
            #    inp_[pointer-view], back = (220, 220, 220), fore = (20, 20, 20))
            pointer_str.add_graphics(AnsiGraphicMode.REVERSE)
        #else:
        #    pointer_str = AStr(inp_[pointer-view])
        
        # insert the pointer into input text at the correct position
        input_plus_pointer = AStr( inp_[:pointer-view]) + pointer_str + AStr(inp_[pointer-view+1:])

        text_c = (50, 200, 50)

        title = AStr(text, fore=text_c)
        fstr = AStr("")
        back_exists = AStr("<", fore=text_c)
        forward_exists = AStr(">", fore=text_c)

        fstr = fstr + (back_exists if view != 0 else AStr(" "))
        fstr = fstr + input_plus_pointer + AStr(" " * (max_input_len - len(input_plus_pointer)))
        fstr = fstr + (forward_exists if view+max_input_len-1 < len(inp) else AStr(" "))

        fstr.add_graphics(AnsiGraphicMode.UNDERLINE)
        return title + fstr

    def on_render(self, drawer: Drawer):
        p = 1
        if self.parent.background_color is not None:
            text_shadow = tuple(map(lambda x: round(x * 0.8), list(self.parent.background_color)))
            drawer.place(AStr(" " * (self.size[0] - (p * 2) - len(self.text)), back=text_shadow), pos=(0, p + len(self.text)), assign = False)
        drawer.place(self.format_textbox(), pos=(0, p), assign = False)