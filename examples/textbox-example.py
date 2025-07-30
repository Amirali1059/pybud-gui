from pybud.session import Session
from pybud.window import Window
from pybud.widgets import TextBox

class Main(Window):
    def __init__(self):
        super().__init__(
            size = (50, 9),
            position = (0, 0),
            title = "TextBox Example",
        )

        self.add_widget(TextBox(
            text = "Enter text: ",
            size = (40, 1),
            position = (5, 4),
        ))

if __name__ == "__main__":
    import asyncio
    
    # only for windows users
    import pybud.drawer.ansi as ansi
    ansi.init()

    # add `Main` to session and show
    s = Session((50, 9), background=(100, 100, 250))
    s.add_window(Main())
    asyncio.run(s.show())