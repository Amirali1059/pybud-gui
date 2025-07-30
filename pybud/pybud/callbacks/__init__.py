from ..drawer import DrawerFast

from ..datatypes import Size, Position

# base class for all callback contexts

class CallbackContext:
    """
    `CallbackContext` stores the callback's identifier, whether or not the callback is cancelled, 
    the result of the callback, and the information that is passed to the callback funtion.
    """

    def __init__(self, id: str = None):
        self.id = id
        self.result = None
        self._is_cancelled = False

    def get_callback_id(self) -> int:
        return self.id
    
    def get_id(self) -> int:
        return self.id
    
    def get_result(self):
        pass
    
    def set_result(self, *args, **kwargs):
        pass

    def cancel(self) -> bool:
        self._is_cancelled = True

    def is_cancelled(self) -> bool:
        return self._is_cancelled

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, result={self.result}, is_cancelled={self._is_cancelled}, ...)"

# actual callback classes

class OnUpdateContext(CallbackContext):
    """
    A child of `CallbackContext` for the update callback with id="on_update".
    """
    
    def __init__(self, tick: int = None, key: str = None):
        super().__init__(id = "on_update")
        self.tick = tick
        self.key = key

    def get_tick(self) -> int:
        return self.tick

    def get_key(self) -> str | None:
        return self.key

class OnDrawContext(CallbackContext):
    """
    A child of `CallbackContext` for screens/widgets callback with id="on_draw".
    """

    def __init__(self, drawer: DrawerFast):
        super().__init__(id = "on_draw")
        self.drawer = drawer

    def get_drawer(self):
        return self.drawer

class OnResizeContext(CallbackContext):
    """
    A child of `CallbackContext` for screens/widgets callback with id="on_resize".
    """

    def __init__(self, size: Size):
        super().__init__(id = "on_resize")
        self.size = size

    def get_drawer(self):
        return self.size


class OnMoveContext(CallbackContext):
    """
    A child of `CallbackContext` for screens/widgets callback with id="on_move".
    """

    def __init__(self, position: Position):
        super().__init__(id = "on_move")
        self.position = position

    def get_drawer(self):
        return self.position

class OnFocusAddedContext(CallbackContext):
    """
    A child of `CallbackContext` for screens/widgets callback with id="on_focus_added".
    """

    def __init__(self):
        super().__init__(id = "on_focus_added")


class OnFocusLostContext(CallbackContext):
    """
    A child of `CallbackContext` for screens/widgets callback with id="on_focus_lost".
    """

    def __init__(self):
        super().__init__(id = "on_focus_lost")


class OnKeyboardInputContext(CallbackContext):
    """
    A child of `CallbackContext` for screens/widgets callback with id="on_keyboard_input".
    """

    def __init__(self, key: str):
        super().__init__(id = "on_keyboard_input")
        assert key is not None, "Expected `key` to be of type `str` but got `None`."
        self.key = key
    
    def get_key(self):
        return self.key