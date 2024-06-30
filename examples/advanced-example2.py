from pybud.drawer.ansi import AnsiGraphicMode
from pybud.drawer.ansi import AnsiString as AStr
from pybud.drawer.color import ColorMode

from pybud.gui.dialog import AutoDialog, DialogBase
from pybud.gui.widgets import WidgetInput, WidgetLabel, WidgetOptions

def input_dialog(WIDTH=76):
    """ the main dialog """

    title = AStr("PyBUD: GUI Beauty", fore = (20, 250, 120))
    title.add_graphics(AnsiGraphicMode.BOLD | AnsiGraphicMode.UNDERLINE)
    
    title = AStr("[ ") + title + AStr(" ]")
    caption = "A python library for creating beautiful GUIs in console, with tons of diffrent components, such as Dialogs, Widgets, Drawables, color optimization, and more!"
    mydialog = AutoDialog(width=WIDTH, ctype=ColorMode.TRUECOLOR, background_color = (90, 110, 220))

    mydialog.add_widget(WidgetLabel(
        title,
        size = [WIDTH, None],  # height will be owerwritten in WidgetLabel
        pos = [0, 1],
    ))
    
    mydialog.add_widget(WidgetLabel(
        caption,
        centered = True,
        size = [WIDTH, None],  # height will be owerwritten in WidgetLabel
        pos = [0, 2],
        padding = 4
    ))

    mydialog.add_widget(WidgetInput(
        "text input: ",
        size = [WIDTH//2 - 4, None],  # height will be owerwritten in WidgetLabel
        pos = [2, 6],
    ))
    mydialog.add_widget(WidgetInput(
        "another text input: ",
        size = [WIDTH//2 - 4, None],  # height will be owerwritten in WidgetLabel
        pos = [WIDTH//2 + 2, 6],
    ))

    def briliant_option(self: DialogBase):
        print("Briliant!         ", end="\r")
        return "Briliant!"

    def verycool_option(self: DialogBase):
        print("Very Cool!        ", end="\r")
        return "Very Cool!"

    def nice_option(self: DialogBase):
        print("Nice!             ", end="\r")
        return "Nice!"

    def awesome_option(self: DialogBase):
        print("Awesome!          ", end="\r")
        return "Awesome!"
    # the text and callback function for each option
    options = [
        ("Nice!", nice_option),
        ("Very Cool!", verycool_option),
        ("Awesome!", awesome_option),
        ("Briliant!", briliant_option),
    ]
    mydialog.add_widget(WidgetOptions(
        options,
        size = [WIDTH-4, None],  # height will be owerwritten in WidgetOptions
        pos = [2, 8],
    ))
    mydialog.add_widget(WidgetLabel(
        AStr("Tip: ", fore = (255, 128, 0)) +
        AStr("you can use TAB or arrow keys to switch between selectable Widgets, use ") + AStr("Ctrl + C", fore = (255, 128, 0)) +
        AStr(" or press enter on text inputs to exit."),
        centered=True,
        size = [WIDTH - 26, None],  # height will be owerwritten in WidgetLabel
        pos = [22, 9],
        name = "LastLabel"
    ))
    return mydialog


if __name__ == "__main__":
    # only for windows users
    import pybud.drawer.ansi as ansi
    ansi.init()

    mydialog = input_dialog()

    #print dialog summery
    #print(mydialog)

    # mydialog.show()
    text = mydialog.show()

    print(f"result (last update return): \"{text}\"")

    print(f"individual outputs:")
    for i, w in enumerate(mydialog.widgets):
        print(w.name + ":")
        if isinstance(w, WidgetInput):
            print(f"text written in textbox ({w.text}): ", w.input)
        elif isinstance(w, WidgetOptions):
            print("selected option id:", w.selected)
            print("selected option text:", w.options[w.selected])
        else:
            print("no output")