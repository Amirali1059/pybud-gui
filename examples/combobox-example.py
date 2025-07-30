from pybud.session import Session
from pybud.window import Window
from pybud.widgets import ComboBox

class Main(Window):
    def __init__(self):
        super().__init__(
            size = (50, 9),
            position = (0, 0),
            title = "ComboBox Example",
        )

        self.add_widget(ComboBox(
            text = "Choose an option: ",
            options = {
                "Option 1": self.option1,
                "Option 2": self.option2,
                "Option 3": self.option3,
            },
            size = (40, 1),
            position = (5, 4),
        ))

    def option1(self):
       print("Option 1 selected")

    def option2(self):
        print("Option 2 selected")

    def option3(self):
        print("Option 3 selected")

if __name__ == "__main__":
    import asyncio
    
    import pybud.drawer.ansi as ansi
    ansi.init()

    s = Session((50, 9), background=(100, 100, 250))
    s.add_window(Main())
    asyncio.run(s.show())