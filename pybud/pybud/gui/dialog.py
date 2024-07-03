# python built-in imports
import time
from threading import Thread
# internal imports
from pybud.drawer import Drawer
from pybud.drawer.ansi import AnsiString as AStr
from pybud.drawer.color import ColorMode
#relative impotrs
from .widgets import WidgetBase
# external imports
try:
    from readchar import key as Key
    from readchar import readkey
except ModuleNotFoundError:
    print("Unable to find 'readchar' package, install it using `pip install readchar`")
    exit(1)

# ticks per second
TPS = 20

class Drawable():
    def __init__(self, ctype: ColorMode = None):
        self.ctype = ColorMode.TRUECOLOR if ctype is None else ctype
        self.width = None
        self.height = None
        self.background_color = None
        self.is_disabled = False
        self.closed = True
        self.drawer: Drawer = None
        self.drawing = False
        self.tick = 0
        # self.last_update = 0
        self.tickupdate_thread: Thread = None
        self.tickupdate_started = False
        self.tick_memory = []

        # holds all callbacks
        self._callbacks = {
            "on_draw": [],
            "on_close": [],
            "on_update": [],
        }

    def assert_callback_id(self, calllback_id):
        assert calllback_id in self._callbacks.keys(), f"callback_id=\"{calllback_id}\" does not exist, available options: {list(self._callbacks.keys())}"

    def add_callback(self, calllback_id: str, fn):
        self.assert_callback_id(calllback_id)
        self._callbacks[calllback_id].append(fn)

    def _run_callback(self, calllback_id: str, **kwargs):
        self.assert_callback_id(calllback_id)
        return [fn(**kwargs) for fn in self._callbacks[calllback_id]]

    def close(self):
        self._run_callback("on_close")

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
            self.close()
        if key == Key.ESC:
            self.close()
        if key == "UPDATE":
            self.tick += 1
        self._run_callback("on_update", key = key)
        self.draw()
        return key

    def do_tick_updates(self):
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

    def do_key_updates(self):
        while not self.closed:
            try:
                key = readkey()
            except KeyboardInterrupt:
                key = Key.CTRL_C
            self.update(key)

    def show(self):
        self.closed = False

        print("\n" * self.height, end="")
        self.draw()

        if not self.tickupdate_started:
            self.tickupdate_thread = Thread(target=self.do_tick_updates)
            self.tickupdate_thread.start()
            self.tickupdate_started = True
        self.do_key_updates()

    def draw(self):
        drawer = Drawer(size=(self.height, self.width), plane_color=self.background_color)
        if not self.closed:
            self.drawing = True
            self._run_callback("on_draw", drawer = drawer)
            self.drawing = False
        print(f"\033[{self.height}F", end="")
        print(drawer.render(self.ctype), end="")
        self.last_draw_time = time.time()


class DialogBase(Drawable):
    def __init__(self, width: int, ctype: ColorMode = None, background_color: tuple[int, int, int] = None):
        super().__init__(ctype)
        self.width = width
        self.background_color = background_color
        self.widgets: list[WidgetBase] = []
        self.set_active_widget(0)
        self.result = None
        self.tick = 0
        self.totw = 0
        self.last_draw_time = time.time()

        self.add_callback("on_update", self._on_update)
        self.add_callback("on_draw", self.draw_widgets)

    def update_height(self):
        max_height = 0
        for w in self.widgets:
            widget_height = w.pos[1] + w.size[1]
            if widget_height > max_height:
                max_height = widget_height

        # set the height to one line more than the end of most buttom added dialog
        self.height = max_height + 1

    def add_widget(self, w: WidgetBase):
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

    def get_active_widget(self):
        i = 0
        w = None

        if self.totw == 0:
            return w, i
        
        for w in self.widgets:
            if not w.selectable:
                continue
            if w.is_disabled:
                i += 1
                continue
            break

        return w, i

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

    def _on_update(self, key):
        w, i = self.get_active_widget()
        if w is not None:
            key = w.update(key)
            self.result = w.result

        if key == Key.TAB:
            self.set_active_widget((i + 1) % self.totw)
        
        return key

    def draw_widgets(self, drawer: Drawer):
        active_w, _ = self.get_active_widget()
        for w in self.widgets:
            border = w is active_w
            drawer.place_drawer(w.render(), (w.pos[1], w.pos[0]), border=border)

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

        self.add_callback("on_draw", self._on_draw_auto)

    def _on_update(self, key):
        key = super()._on_update(key)

        if key == None:
            return

        if self.totw == 0:
            return

        w, i = self.get_active_widget()
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

    def _on_draw_auto(self, drawer: Drawer):
        def get_admination(tick, n = 3, animation = "▁▂▃▄▅▆▆▅▄▃▂▁▂ "):
            rt = tick
            return animation[rt % (len(animation)-n):rt % (len(animation)-n)+n]
            #return round(1 / (time.time() - self.last_draw_time)).__str__()
        drawer.place(AStr(get_admination(self.tick)), pos=(0, 1), assign = False)
