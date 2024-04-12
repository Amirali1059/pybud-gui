
import types

from pybud.drawer import ColoredString as CStr
from pybud.drawer import ColoredStringList as CStrList
from pybud.drawer import ColorType, Drawer
from readchar import key as Key

from ..deftypes import Point, Size, DEFAULT_BACKGROUND_COLOR

def default(d: dict, k:str, default):
    if k in d.keys():
        return d[k]
    else:
        return default

class WidgetBase():
    def __init__(self, size: Size = None, pos: Point = Point(0, 0), **kwargs):
        # set variabled
        self.ctype = default(kwargs, "ctype", ColorType.LEGACY)
        self.size = Size(10, 20) if size is None else size
        self.pos = Point(0, 0) if pos is None else pos
        # defaults
        self.background_color = DEFAULT_BACKGROUND_COLOR
        self.name = default(kwargs, "name", "__name__")
        self.parent = None
        
        self.result = None

    def get_name(self):
        name =  self.__class__.__name__
        c = 0
        for w in self.parent.widgets:
            if isinstance(w, self.__class__):
                c += 1
        return name + "_" + str(c+1)

    
    def on_add(self, parent):
        self.parent = parent
        if self.name == "__name__":
            self.name = self.get_name()

    def on_interrupt(self):
        pass

    def get_drawer(self):
        return Drawer(size=(self.size.getWidth(), self.size.getHeight()), background_color=self.background_color)

    def render(self):
        pass

    def get_render(self):
        self.drawer = self.get_drawer()
        self.render()
        return self.drawer

    def update(self, key):
        return key


class Widget(WidgetBase):
    def __init__(self, size: Size = None, pos: Point = Point(0, 0), **kwargs):
        super().__init__(size, pos, **kwargs)
        # defaults
        self.is_disabled = False
        self.is_selected = False
        self.selectable = True

    def run_callbacks(self):
        pass

    def on_enter(self):
        return self.run_callbacks()

    def on_interrupt(self):
        super().on_interrupt()
        self.is_disabled = True

    def update(self, key):
        key = super().update(key)
        if key == Key.ENTER:
            self.on_enter()
            return
        return key


class WidgetLabel(Widget):
    def __init__(self,
                 text,
                 centered: bool = True,
                 wordwrap: bool = True,
                 size: Size = None,
                 pos: Point = Point(0, 0),
                 **kwargs
                 ):

        super().__init__(size, pos, **kwargs)

        if isinstance(text, str):
            self.text = CStr(text, forecolor=(220, 220, 220))
        elif isinstance(text, CStr) or isinstance(text, CStrList):
            self.text = text
        else:
            raise NotImplementedError()

        self.size.h = (len(text) // (self.size.w - 8)) + 1
        self.centered = centered
        self.wordwrap = wordwrap
        self.selectable = False

    def run_callbacks(self):
        pass

    def _place_text(self, text, ln_idx):
        if self.centered:
            self.drawer.center_place(text, ln_idx=ln_idx)
        else:
            self.drawer.place(text, pos=(0, ln_idx))

    def place_text(self, t, ln_idx):
        #print(t)
        if len(t) > (self.size.getWidth() - 8):
            for i in range(len(t)):
                i_ = len(t) - i - 1
                if i_ > (self.size.getWidth() - 8):
                    continue
                c = t[i_]
                if isinstance(c, str) and c == " ":
                    self._place_text(t[:i_], ln_idx)
                    return self.place_text(t[i_+1:], ln_idx + 1)
                if isinstance(c, CStr) and c.str == " ":
                    self._place_text(t[:i_], ln_idx)
                    return self.place_text(t[i_+1:], ln_idx + 1)
        else:
            self._place_text(t, ln_idx)

    def render(self):
        self.place_text(self.text, ln_idx=0)


class WidgetOptions(Widget):
    def __init__(self,
                 options: list[tuple[str, types.FunctionType]],
                 text: str = "Options:",
                 default_option: int = 0,
                 size: Size = None,
                 pos: Point = Point(0, 0),
                 **kwargs
                 ):

        super().__init__(size, pos, **kwargs)
        self.n_options = len(options)
        self.options = list(map(lambda x: x[0], options))
        self.text = text
        self.callbacks = list(map(lambda x: x[1], options))
        self.selected = default_option
        self.size.h = 1 + self.n_options

    def run_callbacks(self):
        self.result = self.callbacks[self.selected](self.parent)
        return self.result

    def update(self, key):
        key = super().update(key)
        if key == Key.UP:
            self.selected = (self.selected - 1) % self.n_options
            return
        if key == Key.DOWN:
            self.selected = (self.selected + 1) % self.n_options
            return
        return key

    def render(self):
        caption_start = 2
        __options = self.text.ljust(self.size.getWidth()-caption_start)
        self.drawer.place(CStr(__options, forecolor=(
            220, 220, 220)), pos=(caption_start, 0))
        for i, option in enumerate(self.options):
            if i == self.selected:
                option_color = (50, 220, 80)
                option_indicator = CStr("> ", forecolor=(220, 220, 220))
            else:
                option_color = (220, 220, 220)
                option_indicator = CStr("  ", forecolor=(220, 220, 220))
            __option = CStr(option, forecolor=option_color)
            self.drawer.place(option_indicator + __option,
                              pos=(caption_start, 1 + i))


class WidgetInput(Widget):
    def __init__(self,
                 text: str,
                 size: Size = None,
                 pos: Point = Point(0, 0),
                 **kwargs
                 ):
        super().__init__(size, pos, **kwargs)
        # p = 1
        self.size.h = 1
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
        ignored_keys = [
            Key.CR,
            Key.DOWN,
            Key.UP,
            Key.LEFT,
            Key.RIGHT,
            Key.END,
            Key.HOME,
            Key.ESC,
            Key.ESC_2,
            Key.ENTER,
            Key.ENTER_2,
            Key.INSERT,
            Key.LF,
            Key.PAGE_DOWN, 
            Key.PAGE_UP, 
            Key.SUPR,
        ]

        self.__ignored_keys = ctrl_keys + funcion_keys + ignored_keys

    def run_callbacks(self):
        super().run_callbacks()
        self.parent.close()
        self.result = self.input
        return self.result

    def reset(self):
        self.input = ""
        self.pointer = 0
        self.view = 0

    def get_max_length(self):
        p = 2
        max_input_len = self.size.getWidth()-(p * 2)-len(self.text)
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
                self.input = self.input[:self.pointer -
                                        1] + self.input[self.pointer:]
            else:
                self.input = self.input[self.pointer:]
            self.pointer = max(self.pointer - 1, 0)
            if self.pointer-self.view < 0:
                self.view = max(self.view - max_input_len, 0)
            return

        # delete
        if key == Key.DELETE:
            self.input = self.input[:self.pointer] + \
                self.input[self.pointer+1:]
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

        if not self.is_disabled and self.show_pointer or inp_[pointer-view] != " ":
            pointer_str = CStr(
                inp_[pointer-view], backcolor=(220, 220, 220), forecolor=(20, 20, 20))
        else:
            pointer_str = CStr(inp_[pointer-view])
        # insert the pointer into input text at the correct position
        input_plus_pointer = CStr(
            inp_[:pointer-view]) + pointer_str + CStr(inp_[pointer-view+1:])

        text_c = (50, 200, 50)

        fstr = CStr(text, forecolor=text_c)

        back_exists = CStr("<", forecolor=text_c)
        forward_exists = CStr(">", forecolor=text_c)

        fstr += (back_exists if view != 0 else " ")
        fstr += input_plus_pointer + " " * \
            (max_input_len - len(input_plus_pointer))
        fstr += (forward_exists if view+max_input_len-1 < len(inp) else " ")

        return fstr

    def render(self):
        p = 1
        if self.parent.background_color is not None:
            text_shadow = tuple(map(lambda x: x * 0.8, list(self.parent.background_color)))
            self.drawer.place(CStr(" " * (self.size.getWidth() - (p * 2) - len(self.text)), backcolor=text_shadow), pos=(p + len(self.text), 0))
        self.drawer.place(self.format_textbox(), pos=(p, 0))
        #self.drawer.write_text(str(text_shadow), pos=(0, 0))
