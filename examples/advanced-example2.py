import pybud as pb

class Main(pb.Window):
    def __init__(self):
        super().__init__(
            size = (76, 14),
            position = (0, 0),
            title = "PyBUD: GUI Beauty"
        )
        
        title = pb.ansi.AnsiString("PyBUD: GUI Beauty", fore = (20, 250, 120))
        title.add_graphics(pb.ansi.AnsiGraphicMode.BOLD | pb.ansi.AnsiGraphicMode.UNDERLINE)
        
        title = pb.ansi.AnsiString("[ ") + title + pb.ansi.AnsiString(" ]")

        self.add_widget(pb.widgets.Label(
            title,
            centered = True,
            size = (self.size.width - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (2, 1),
        ))
        
        caption = "A python library for creating beautiful GUIs in console, with tons of diffrent components, such as Dialogs, Widgets, Drawables, ansi color optimizations written in Rust, and more!"
        
        self.add_widget(pb.widgets.Label(
            caption,
            centered = True,
            size = (self.size.width - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (2, 2),
        ))
        self.add_widget(pb.widgets.TextBox(
            "TextBox: ",
            size = (self.size.width//2 - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (2, 6),
        ))
        self.add_widget(pb.widgets.ComboBox(
            "ComboBox: ",
            options = {
                "Nice!": self.nice_option,
                "Great!": self.great_option,
                "Awesome!": self.awesome_option,
                "Briliant!": self.briliant_option,
            },
            size = (self.size.width//2 - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (self.size.width//2 + 2, 6),
        ))
        self.add_widget(pb.widgets.VerticalMultipleChoice(
            "VerticalMultipleChoice:",
            # the text and callback function for each option
            options = {
                "Nice!": self.nice_option,
                "Great!": self.great_option,
                "Awesome!": self.awesome_option,
                "Briliant!": self.briliant_option,
            },
            size = (self.size.width-4, 1),  # height will be owerwritten in WidgetOptions
            position = (2, 8),
        ))
        self.add_widget(pb.widgets.Label(
            pb.ansi.AnsiString("Tip: ", fore = (255, 128, 0)) +
            pb.ansi.AnsiString("Use TAB or arrow keys to switch between Widgets, Use ") +
            pb.ansi.AnsiString("Ctrl + C", fore = (255, 128, 0)) + pb.ansi.AnsiString(" to exit the demo."),
            centered = True,
            size = (self.size.width - 26, 1),  # height will be owerwritten in WidgetLabel
            position = (22, 9),
            name = "tip-label"
        ))
        self.lbl_result = pb.widgets.Label(
            "",
            centered = True,
            size = (self.size.width - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (2, 12),
            name = "result-label"
        )
        self.add_widget(self.lbl_result)

    def briliant_option(self):
        self.lbl_result.text = "Briliant!"

    def great_option(self):
        self.lbl_result.text = "great!"

    def nice_option(self):
        self.lbl_result.text = "Nice!"

    def awesome_option(self):
        self.lbl_result.text = "Awesome!"


if __name__ == "__main__":
    import asyncio
    
    # only for windows users
    pb.ansi.init()
    
    # define `Session` size and `Session` background, you can think of 
    # a session as the screen display that shows the `Window`s on it.
    s = pb.Session((76, 14), background=(90, 110, 220))
    s.add_window(Main())
    asyncio.run(s.show())

    print(f"Session Closed!")
    for i, w in enumerate(s.window_buffer[0]._widgets):
        print(w.name + ":")
        if isinstance(w, pb.widgets.TextBox):
            print(f"- text=\"{w.text}\", input=\"{w.input}\"")
        elif isinstance(w, (pb.widgets.VerticalMultipleChoice, pb.widgets.ComboBox)):
            print(f"- selected_option_id={w.selected_option_id}")
            print(f"- selected option text=\"{list(w.options)[w.selected_option_id]}\"")
        if isinstance(w, pb.widgets.Label):
            print(f"- text=\"{w.text}\"")
        else:
            print("- no data")
        print("")