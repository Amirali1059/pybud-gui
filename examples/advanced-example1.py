import pybud.ansi as ansi
from pybud.drawing import ColoredString as CStr
from pybud.ansi import ColorType
from pybud.gui.dialog import AutoDialog
from pybud.deftypes import Size, Point
from pybud.gui.widgets import WidgetLabel, WidgetOptions


def main_dialog(WIDTH = 70):
    """ the main dialog """

    def briliant_option(self):
        ansi.write("Briliant!        \r")
        ansi.flush()
        return "Briliant!"

    def verycool_option(self):
        ansi.write("Very Cool!        \r")
        ansi.flush()
        return "Very Cool!"

    def nice_option(self):
        ansi.write("Nice!             \r")
        ansi.flush()
        return "Nice!"

    title = CStr("[") + CStr(" " + "PyBUD: GUI Beauty" +
                             " ", forecolor=(255, 0, 0)) + CStr("]")
    caption = "A python library for creating beautiful GUIs in console, with tons of diffrent components, such as Dialogs, Widgets, Drawables, optimized colored strings, and more!"
    options = [
        ("Nice!", nice_option),
        ("Very Cool!", verycool_option),
        ("Briliant!", briliant_option),
    ]
    default = 2
    mydialog = AutoDialog(width=WIDTH, ctype=ColorType.LEGACY)
    mydialog.add_widget(WidgetLabel(
        title,
        size=Size(WIDTH, 0),  # height will be owerwritten in WidgetLabel
        pos=Point(0, 1),
    ))
    mydialog.add_widget(WidgetLabel(
        text = caption,
        centered=False,
        size=Size(WIDTH, 0),  # height will be owerwritten in WidgetLabel
        pos=Point(4, 2),
    ))

    mydialog.add_widget(WidgetOptions(
        options,
        default_option=default,
        size=Size(WIDTH-4, 0),  # height will be owerwritten in WidgetOptions
        pos=Point(2, 6),
    ))

    return mydialog

if __name__ == "__main__":
    ansi.InitAnsi()

    mydialog = main_dialog()
    try:
        text = mydialog.show()

        print(f"result: \"{text}\"")
        
    except KeyboardInterrupt:
        mydialog.close()