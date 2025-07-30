import pybud as pb
import pybud.widgets as pbw

class Main(pb.Window):
    def __init__(self):
        super().__init__(
            size = (76, 14),
            position = (0, 0),
            title = "PyBUD: GUI Beauty"
        )
        
        title = pb.ansi.AnsiString("PyBUD: GUI Beauty", fore = (20, 250, 120))
        title.add_graphics(pb.ansi.AnsiGraphicMode.BOLD | pb.ansi.AnsiGraphicMode.UNDERLINE)
        self.lbl_title = pb.widgets.Label(
            pb.ansi.AnsiString("[ ") + title + pb.ansi.AnsiString(" ]"),
            centered = True,
            size = (self.size.width - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (2, 1),
        )
        self.add_widget(self.lbl_title)
        
        self.lbl_caption = pbw.Label(
            "A python library for creating beautiful GUIs in console, with tons of diffrent components, such as Dialogs, Widgets, Drawables, ansi color optimizations written in Rust, and more!",
            centered = True,
            size = (self.size.width - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (2, 2),
        )
        self.add_widget(self.lbl_caption)
        
        self.tbox_input = pbw.TextBox(
            "TextBox: ",
            size = (self.size.width//2 - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (2, 6),
        )
        self.add_widget(self.tbox_input)

        self.cbox_input = pbw.ComboBox(
            "ComboBox: ",
            options = {
                "Nice!": self.nice_option,
                "Great!": self.great_option,
                "Awesome!": self.awesome_option,
                "Briliant!": self.briliant_option,
            },
            size = (self.size.width//2 - 4, 1),  # height will be overwritten in WidgetLabel
            position = (self.size.width//2 + 2, 6),
        )
        self.add_widget(self.cbox_input)

        self.vmc_input = pbw.VerticalMultipleChoice(
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
        )
        self.add_widget(self.vmc_input)

        self.lbl_tip = pbw.Label(
            pb.ansi.AnsiString("Tip: ", fore = (255, 128, 0)) +
            pb.ansi.AnsiString("Use TAB or arrow keys to switch between Widgets, Use ") +
            pb.ansi.AnsiString("Ctrl + C", fore = (255, 128, 0)) + pb.ansi.AnsiString(" to exit the demo."),
            centered = True,
            size = (self.size.width - 26, 1),  # height will be owerwritten in WidgetLabel
            position = (22, 9),
            name = "tip-label"
        )
        self.add_widget(self.lbl_tip)
        
        self.lbl_result = pbw.Label(
            "",
            centered = True,
            size = (self.size.width - 4, 1),  # height will be owerwritten in WidgetLabel
            position = (2, 12),
            name = "result-label"
        )
        self.add_widget(self.lbl_result)
        
        # resize all widgets based on the window size
        self.on_resize(context=pb.callbacks.OnResizeContext(self.size))

    def briliant_option(self):
        self.lbl_result.text = pb.ansi.AnsiString("Briliant!", fore=(255, 128, 0))

    def great_option(self):
        self.lbl_result.text = pb.ansi.AnsiString("Great!", fore=(0, 255, 128))

    def nice_option(self):
        self.lbl_result.text = pb.ansi.AnsiString("Nice!", fore=(255, 0, 0))

    def awesome_option(self):
        self.lbl_result.text = pb.ansi.AnsiString("Awesome!", fore=(255, 255, 0))
    
    def on_resize(self, context: pb.callbacks.OnResizeContext):
        self.lbl_title.size.width = context.size.width - 4
        self.lbl_caption.size.width = context.size.width - 4
        self.tbox_input.size.width = context.size.width//2 - 4
        self.cbox_input.position.x = context.size.width//2 + 2
        self.cbox_input.size.width = context.size.width//2 - 4
        self.vmc_input.size.width = context.size.width-4
        
        self.lbl_result.position.y = context.size.height - 2
        self.lbl_result.size.width = context.size.width - 4
        
        self.lbl_tip.position = pb.datatypes.Position(context.size.width//2 - 11, 9)
        self.lbl_tip.size.width = context.size.width - self.lbl_tip.position.x - 4


if __name__ == "__main__":
    import asyncio
    
    # only for windows users
    pb.ansi.init()
    
    # enable experimental features (might not work in all environments)
    pb.enable_experimental_features()
    
    # define `Session` size and `Session` background, you can think of 
    # a session as the screen display that shows the `Window`s on it.
    s = pb.Session((76, 14), background=(90, 110, 220), allow_resize=True)
    s.add_window(Main())
    asyncio.run(s.show())

    print(f"Session Closed!")
    for i, w in enumerate(s.window_buffer[0]._widgets):
        print(w.name + ":")
        if isinstance(w, pbw.TextBox):
            print(f"- text=\"{w.text}\", input=\"{w.input}\"")
        elif isinstance(w, (pbw.VerticalMultipleChoice, pbw.ComboBox)):
            print(f"- selected_option_id={w.selected_option_id}")
            print(f"- selected option text=\"{list(w.options)[w.selected_option_id]}\"")
        if isinstance(w, pbw.Label):
            print(f"- text=\"{w.text}\"")
        else:
            print("- no data")
        print("")