import time
import os
import warnings
import asyncio

from readchar import key as KeyPress
from readchar import readkey

from .drawer import DrawerFast, color, ansi
from .window import Window

from .datatypes import Size, Color

from .callbacks import OnUpdateContext

EXPERIMENTAL_FEATURES = False


def enable_experimental_features():
    global EXPERIMENTAL_FEATURES
    EXPERIMENTAL_FEATURES = True


def get_admination_at(tick, n=3, animation="▁▂▃▄▅▆▆▅▄▃▂▁▂ "):
    return animation[tick % (len(animation)-n):tick % (len(animation)-n)+n]

# https://stackoverflow.com/a/55505152


async def repeat_periodically(interval, func, *args, **kwargs):
    """Run func every interval seconds.

    If func has not finished before *interval*, will run again
    immediately when the previous iteration finished.

    *args and **kwargs are passed as the arguments to func.
    """
    while True:
        await asyncio.gather(
            func(*args, **kwargs),
            asyncio.sleep(interval),
        )


class UpdateHandler:
    def __init__(self, update_fn, tps: int = 20):
        self.tps = tps
        self.closed = False
        self.tick = 0

        self.tickupdate_task: asyncio.Task = None
        self.keyupdate_task: asyncio.Task = None

        self.update_fn = update_fn

    async def start(self):
        self.tickupdate_task = asyncio.create_task(self.do_tick_updates())
        self.keyupdate_task = asyncio.create_task(self.do_key_updates())

    async def stop(self):
        self.tickupdate_task.cancel()
        self.keyupdate_task.cancel()
        self.tickupdate_task = None
        self.keyupdate_task = None
        self.closed = True

    def is_running(self):
        return not self.closed

    async def do_tick_updates(self):
        self.tick = 0

        async def tick():
            if self.closed:
                return
            await self.update_fn(OnUpdateContext(self.tick))
            self.tick += 1

        await repeat_periodically(interval = 1/self.tps, func = tick)

    async def do_key_updates(self):
        while not self.closed:
            try:
                key = await asyncio.get_running_loop().run_in_executor(None, readkey)
            except KeyboardInterrupt:
                key = KeyPress.CTRL_C
            if self.closed:
                break
            await self.update_fn(OnUpdateContext(self.tick, key=key))
    
    async def run_until_finished(self):
        await self.start()
        while self.is_running():
            await asyncio.sleep(0.01)


class Session:
    """
    A `Session` is main handler for all `Window`s, each `Session` contains a list of ordered windows.

    Additonally creates a `Drawer` instance and draws `Window`s in order,
    Also, adds functionality for a `Window` to appear on top of other `Window`s,
    Lastly, handles keyboard updates and tick updates for all windows with an instance of `UpdateHandler`.
    """

    def __init__(
        self,
        size: Size | tuple[int, int],
        background: Color | tuple[int, int, int],
        color_mode: color.ColorMode = None,
        allow_resize: bool = False
    ):
        if not isinstance(size, (Size, tuple)):
            raise TypeError(
                f"Expected size to be of type `datatypes.Size` or `tuple[int, int]` but got {type(size)}."
            )
        if isinstance(size, tuple):
            size = Size(*size)

        self.size = size

        if not isinstance(background, (Color, tuple)):
            raise TypeError(
                f"Expected background to be of type `datatypes.Color` or `tuple[int, int, int]` but got {type(background)}."
            )
        if isinstance(background, tuple):
            background = Color(*background)

        self.background = background

        if allow_resize:
            if EXPERIMENTAL_FEATURES:
                warnings.warn("`allow_resize` is experimental and might be changed in a future update.")
            else:
                raise NotImplementedError(
                    "`allow_resize` is not yet stable but will be added in a future update, to use unstable features add `pybud.enable_experimental_features()` to the start of your code.")

        self.allow_resize = allow_resize

        self.color_mode = color.ColorMode.TRUECOLOR if color_mode is None else color_mode

        self.update_handler = UpdateHandler(update_fn=self.update)

        self.window_buffer: list[Window] = []

        self.drawer = self.__init_new_drawer()

        self.draw_lock = asyncio.locks.Lock()

    def __init_new_drawer(self) -> DrawerFast:
        return DrawerFast(
            width=self.size.width,
            height=self.size.height,
            plane_color=color.AnsiColor(*self.background.get_rgb())
        )
    
    def add_window(self, window: Window):
        if window in self.window_buffer:
            self.window_buffer.remove(window)
        self.window_buffer.append(window)
        self.bring_window_to_front(window)
        self.update_focus()

    def bring_window_to_front(self, window: Window):
        for w in self.window_buffer:
            w._set_depth(0 if w is window else 1+w._get_depth())

    def update_focus(self):
        for i, window in enumerate(self.window_buffer):
            if (i + 1) == len(self.window_buffer):
                window.focus()
            else:
                window.unfocus()

    def __enable_draw_mode(self):
        if EXPERIMENTAL_FEATURES:
            print("\033[?1049h\033[?25l", end="")

    def __disable_draw_mode(self):
        if EXPERIMENTAL_FEATURES:
            print("\033[?1049l\033[?25h", end="")

    async def show(self):
        self.__enable_draw_mode()
        for window in self.window_buffer:
            window.open()
        await self.update_handler.run_until_finished()

    async def close(self):
        print(("\r" + (" " * self.size.width) + "\n") * (self.size.height), end="")
        print(f"\033[{self.size.height}F", end="")
        await self.update_handler.stop()
        self.__disable_draw_mode()

    def __resize_to_terminal(self):
        if EXPERIMENTAL_FEATURES:
            self.resize(Size(*os.get_terminal_size()))

    def resize(self, size=None):
        if size is None:
            size = self.size
        if not isinstance(size, (Size, tuple)):
            raise TypeError(
                f"Expected size to be of type `datatypes.Size` or `tuple[int, int]` but got {type(size)}."
            )
        if isinstance(size, tuple):
            size = Size(*size)
        self.size = size
        self.drawer = self.__init_new_drawer()
        for window in self.window_buffer:
            window.resize(size)

    async def update(self, context: OnUpdateContext):
        self.__resize_to_terminal()
        for window in reversed(self.window_buffer):
            if window.is_in_focus:
                window.update(context)
        await self.draw()

    def clear(self):
        self.drawer.fill(self.background)

    async def draw(self):
        await self.draw_lock.acquire()

        any_window_is_open = False
        for window in sorted(self.window_buffer, key=lambda x: x._get_depth()):
            if window.is_open:
                any_window_is_open = True
                self.drawer.place_plane(
                    window.draw(),
                    posx = window.position.x,
                    posy = window.position.y
                )

        if not any_window_is_open:
            await self.close()
            return

        self.drawer.text(get_admination_at(self.update_handler.tick), self.size.width-4, 0)
        print(self.drawer.render(self.color_mode), end="")
        print(f"\033[{self.size.height-1}F", end="")
        
        self.draw_lock.release()

