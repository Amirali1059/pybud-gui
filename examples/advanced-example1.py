from pybud.drawer.ansi import AnsiGraphicMode
from pybud.drawer.ansi import AnsiString as AStr
from pybud.drawer.color import ColorMode
from pybud.gui.dialog import AutoDialog
from pybud.gui.widgets import WidgetLabel, WidgetOptions


def main_dialog(WIDTH = 76):
    """ the main dialog """

    def briliant_option(self):
        print("Briliant!         ", end="\r")
        return "Briliant!"

    def verycool_option(self):
        print("Very Cool!        ", end="\r")
        return "Very Cool!"

    def nice_option(self):
        print("Nice!             ", end="\r")
        return "Nice!"

    title = AStr("PyBUD: GUI Beauty", fore = (20, 250, 120))
    title.add_graphics(AnsiGraphicMode.BOLD)
    
    title = AStr("[ ") + title + AStr(" ]")
    caption = "A python library for creating beautiful GUIs in console, with tons of diffrent components, such as Dialogs, Widgets, Drawables, color optimization, and more!"
    mydialog = AutoDialog(width=WIDTH, ctype=ColorMode.TRUECOLOR, background_color = (90, 110, 220))

    options = [
        ("Nice!", nice_option),
        ("Very Cool!", verycool_option),
        ("Briliant!", briliant_option),
    ]
    default = 2
    mydialog.add_widget(WidgetLabel(
        title,
        size=[WIDTH, None],  # height will be owerwritten in WidgetLabel
        pos=[0, 1],
    ))

    mydialog.add_widget(WidgetLabel(
        caption,
        centered = True,
        size = [WIDTH, None],  # height will be owerwritten in WidgetLabel
        pos = [0, 2],
        padding = 4
    ))

    mydialog.add_widget(WidgetOptions(
        options,
        default_option=default,
        size = [WIDTH-4, None],  # height will be owerwritten in WidgetOptions
        pos = [2, 6],
    ))

    return mydialog

if __name__ == "__main__":
    #ansi.InitAnsi()

    mydialog = main_dialog()
    try:
        text = mydialog.show()

        print(f"result: \"{text}\"")
        
    except KeyboardInterrupt:
        mydialog.close()