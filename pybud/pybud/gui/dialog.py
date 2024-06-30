# python built-in imports
import time
from threading import Thread
# internal imports
from pybud.drawer import Drawer
from pybud.drawer.ansi import AnsiString as AStr
from pybud.drawer.color import ColorMode
#relative impotrs
from .widgets import Widget
# external imports
try:
    from readchar import key as Key
    from readchar import readkey
except ModuleNotFoundError:
    print("Unable to find 'readchar' package, install it using `pip install readchar`")
    exit(1)

DEFAULT_BACKGROUND_COLOR = (110, 90, 250)

LAST_SHOWN_DRAWABLE = None
# ticks per second
TPS = 20

class Drawable():
    def __init__(self, ctype: ColorMode = None):
        self.ctype = ColorMode.TRUECOLOR if ctype is None else ctype
        self.width = None
        self.height = None
        self.background_color = DEFAULT_BACKGROUND_COLOR
        self.is_disabled = False
        self.closed = True
        self.drawer: Drawer = None
        self.drawing = False
        # self.last_update = 0
        self.tickupdate_thread: Thread = None
        self.tickupdate_started = False
        self.tick_memory = []

    def onClose(self):
        self.close()

    def close(self):
        self.closed = True
        while self.tickupdate_thread.is_alive():
            time.sleep(0.01)
        self.tickupdate_started = False
        print(f"\033[{self.height}F", end = "")        
        print(("\n" + " " * self.width) * (self.height), end = "")
        print("\033M" * self.height, end = "\r")
        print(" " * self.width + "\033M")

    def update(self, key: str):
        if key == Key.CTRL_C:
            self.onClose()
        if key == Key.ESC:
            self.onClose()
        return key

    def doTickUpdates(self):
        while not self.closed:
            # records the delay caused by an update and subtracts
            # that from tick waiting time.  
            t = time.time()
            self.update("UPDATE")
            real_delay = (time.time() - t) 
            self.tick_memory.append(real_delay)
            self.tick_memory = self.tick_memory[-5:]

            frame_time = (1 / TPS) - (sum(self.tick_memory) / len(self.tick_memory))

            time.sleep(max(0, frame_time))

    def doKeyUpdates(self):
        while not self.closed:
            try:
                key = readkey()
            except KeyboardInterrupt:
                key = Key.CTRL_C
            self.update(key)

    def show(self):
        global LAST_SHOWN_DRAWABLE
        LAST_SHOWN_DRAWABLE = self

        self.closed = False

        print("\n" * self.height, end="")
        self.draw()

        if not self.tickupdate_started:
            self.tickupdate_thread = Thread(target=self.doTickUpdates)
            self.tickupdate_thread.start()
            self.tickupdate_started = True
        self.doKeyUpdates()

    def get_drawer(self):
        return Drawer(size=(self.height, self.width), plane_color=self.background_color)

    def draw(self):
        if not self.closed:
            self.drawing = True
            self.drawer = self.get_drawer()


class DialogBase(Drawable):
    def __init__(self, width: int, ctype: ColorMode = None, background_color: tuple[int, int, int] = None):
        super().__init__(ctype)
        self.width = width
        self.background_color = background_color
        self.widgets: list[Widget] = []
        self.set_active_widget(0)
        self.result = None
        self.tick = 0
        self.totw = 0
        self.last_draw_time = time.time()

    def update_height(self):
        max_height = 0
        for w in self.widgets:
            widget_height = w.pos[1] + w.size[1]
            if widget_height > max_height:
                max_height = widget_height

        # set the height to one line more than the end of most buttom added dialog
        self.height = max_height + 1

    def add_widget(self, w: Widget):
        w.on_add(self)
        w.background_color = self.background_color
        self.widgets.append(w)
        # self.height += w.size.getHeight()
        self.update_height()
        self.totw = self.get_total_selectable_widgets()

    def get_total_selectable_widgets(self):
        i = 0
        for w in self.widgets:
            if w.selectable:
                i += 1
        return i

    def get_active_widget(self, return_i: bool = False):
        i = 0
        w = None

        if self.totw == 0:
            if return_i:
                return w, i
            else:
                return w
        
        for w in self.widgets:
            if not w.selectable:
                continue
            if w.is_disabled:
                i += 1
                continue
            break

        if return_i:
            return w, i
        else:
            return w

    def set_active_widget(self, __i: int):
        i = 0
        for w in self.widgets:
            if not w.selectable:
                continue

            if i == __i:
                w.is_disabled = False
            else:
                w.is_disabled = True
            i += 1

    def update(self, key, draw=True):
        key = super().update(key)

        w, i = self.get_active_widget(True)
        if w is not None:
            key = w.update(key)
            self.result = w.result

        if key == Key.TAB:
            self.set_active_widget((i + 1) % self.totw)

        if key == "UPDATE":
            self.tick += 1

        if draw and key == "UPDATE":
            self.draw()
        else:
            return key

    def draw_widgets(self, drawer: Drawer):
        active_w = self.get_active_widget()
        for w in self.widgets:
            
            border = w is active_w
            w_render = w.get_render()
            drawer.place_drawer(
                w_render, (w.pos[1], w.pos[0]), border=border)
        return drawer

    def render(self):
        self.drawer = self.draw_widgets(self.drawer)

    def draw(self):
        if self.closed or self.drawing:
            return
        super().draw()
        self.render()

        print(f"\033[{self.height}F", end="")
        print(self.drawer.render(self.ctype), end="")
        # time.sleep(0.01)
        self.drawing = False
        self.last_draw_time = time.time()

    def show(self):
        super().show()
        return self.result

    def __str__(self):
        s = "+ " + self.__class__.__name__ + ":\n"
        for w in self.widgets:
            s += "|   " + w.name + "\n"
        return s


class AutoDialog(DialogBase):
    def __init__(self, width: int, ctype: ColorMode = None, background_color: tuple[int, int, int] = None, mode: str = "v"):
        super().__init__(width, ctype)
        assert mode in ["v", "iv", "h", "ih"], f"Unknown mode \"{mode}\"!"
        self.mode = mode.lower()
        self.background_color = background_color

    def update(self, key):
        key = super().update(key, draw=False)
        if key == None:
            self.draw()
            return

        if self.totw != 0:
            w, i = self.get_active_widget(True)
            av = i
            if self.mode == "v":
                if key == Key.UP:
                    av = (i - 1) % self.totw 
                elif key == Key.DOWN:
                    av = (i + 1) % self.totw
            elif self.mode == "iv":
                if key == Key.DOWN:
                    av = (i + 1) % self.totw
                elif key == Key.UP:
                    av = (i + 1) % self.totw
            elif self.mode == "h":
                if key == Key.LEFT:
                    av = (i - 1) % self.totw
                elif key == Key.RIGHT:
                    av = (i + 1) % self.totw
            elif self.mode == "ih":
                if key == Key.RIGHT:
                    av = (i + 1) % self.totw
                elif key == Key.LEFT:
                    av = (i - 1) % self.totw
            else:
                raise ValueError(f"Unknown mode \"{self.mode}\"!")
            self.set_active_widget(av)
        
        # draw after each update
        self.draw()

    def render(self):
        super().render()
        animation = "▁▂▃▄▅▆▆▅▄▃▂▁▂ "

        def get_admination(tick, n=3):
            rt = tick
            return animation[rt % (len(animation)-n):rt % (len(animation)-n)+n]
            #return round(1 / (time.time() - self.last_draw_time)).__str__()
        self.drawer.place(AStr(get_admination(self.tick)), pos=(0, 1), assign = False)

    def show(self):
        super().show()
        return self.result
