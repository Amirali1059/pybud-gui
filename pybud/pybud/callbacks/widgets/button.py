from .. import CallbackContext

class OnButtonPress(CallbackContext):
    """
    A child of `CallbackContext` for widgets initializing callback with id="on_button_press".
    """

    def __init__(self):
        super().__init__(id = "on_button_press")