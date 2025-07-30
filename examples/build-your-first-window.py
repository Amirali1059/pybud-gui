# import the main session class
from pybud.session import Session
# import the main window class
from pybud.window import Window

# build the main window
class Main(Window):
    def __init__(self):
        super().__init__(
            size = (100, 10),
            position = (0, 0),
            title = "Window Example",
        )

if __name__ == "__main__":
    import asyncio
    
    # only for windows users
    import pybud.drawer.ansi as ansi
    ansi.init()
    
    # define `Session` size and `Session` background, you can think of 
    # a session as the screen display that shows the `Window`s on it.
    s = Session((100, 10), background=(100, 100, 250))
    s.add_window(Main())
    asyncio.run(s.show())
    print("Closed!")