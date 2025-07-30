from pybud.drawer import ansi
from pybud.session import Session
from pybud.window import Window
from pybud.widgets import Label, VerticalMultipleChoice

class Main(Window):
    def __init__(self):
        super().__init__(
            size = (76, 11),
            position = (0, 0),
            title = "PyBUD: GUI Beauty" # ansi.AnsiString("PyBUD: GUI Beauty", fore = (20, 250, 120))
        )
        
        caption = "A python library for creating beautiful GUIs in console, with tons of diffrent components, such as Dialogs, Widgets, Drawables, ansi color optimizations written in Rust, and more!"
        
        self.add_widget(Label(
            ansi.AnsiString(caption, fore=(150, 250, 50)),
            centered = True,
            # height will be owerwritten but the inirial height has to be at least 1
            size = (self.size.width -4, 1),
            position = (2, 1),
        ))
        
        self.add_widget(VerticalMultipleChoice(
            text = ansi.AnsiString("VerticalMultipleChoice: ", fore=(150, 250, 50)),
            options = {
                "Nice!": self.nice_option,
                "Very Good!": self.verygood_option,
                "Briliant!": self.briliant_option,
            },
            default_option = 2,
            # height will be owerwritten but the inirial height has to be at least 1
            size = (self.size.width - 4, 1),
            position = (2, 5),
        ))
        self.lbl_result = Label(
            "",
            centered = True,
            # height will be owerwritten but the inirial height has to be at least 1
            size = (self.size.width -2, 1),
            position = (1, 9),
        )
        self.add_widget(self.lbl_result)

    def briliant_option(self):
        self.lbl_result.text = ansi.AnsiString("Briliant!", fore=(0, 255, 0))

    def verygood_option(self):
        self.lbl_result.text = ansi.AnsiString("Very Good!", fore=(255, 0, 0))

    def nice_option(self):
        self.lbl_result.text = ansi.AnsiString("Nice!", fore=(0, 0, 255))

if __name__ == "__main__":
    import asyncio
    
    # only for windows users
    import pybud.drawer.ansi as ansi
    ansi.init()
    
    # define `Session` size and `Session` background, you can think of 
    # a session as the screen display that shows the `Window`s on it.
    s = Session((76, 11), background=(90, 110, 220))
    s.add_window(Main())
    asyncio.run(s.show())
    print("Closed!")