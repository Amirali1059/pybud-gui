# import the main session class
from pybud.session import Session
# import the main window class
from pybud.window import Window
# import widgets
from pybud.widgets import Label
# import `ansi` (using this module you can define text with color)
from pybud.drawer import ansi

# build the main window
class Main(Window):
    def __init__(self):
        super().__init__(
            size = (100, 10),
            position = (0, 0),
            title = "Widget Example",
        )

        # add a label widget, set text, width and position
        self.add_widget(Label(
            # define a ansi.AnsiString object that renders text with colors
            # you can set both forecolor and backcolor
            text = ansi.AnsiString("Hello world!", fore = (90, 250, 90)),
            position = (44, 4),
            size = (60, 1)
            )
        )

if __name__ == "__main__":
    import asyncio
    
    # only for windows users
    import pybud.drawer.ansi as ansi
    ansi.init()
    
    # define `Session` size and `Session` background, you can think of 
    # a session as the screen display that shows the `Window`s on it.
    s = Session((100, 9), background=(100, 100, 250))
    s.add_window(Main())
    asyncio.run(s.show())

    print("Closed!")