# PyBUD: python beauty
**A python library for creating beautiful GUIs in console, with tons of diffrent components, such as Dialouges, Widgets, Drawables, color optimization, and more!**
## example usage:
```python
import pybud
import pybud.ansi as ansi
from pybud.ansi import ColorType
from pybud.drawer import ColoredString as CStr
from pybud.gui.gui import AutoDialouge
from pybud.gui.utils import Point, Size
from pybud.gui.widgets import WidgetInput, WidgetLabel, WidgetOptions

# callback functions
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

def awesome_option(self):
    ansi.write("Awesome!          \r")
    ansi.flush()
    return "Awesome!"


def main_dialouge(WIDTH=76):
    """ the main dialouge """
    # you can use `CStr`s to define colord text!
    title = CStr("[") + CStr(" PyBUD: GUI Beauty ", forecolor=(255, 0, 0)) + CStr("]")
    # you can also use the built in str
    caption = "A python library for creating beautiful GUIs in console, with tons of diffrent components, such as Dialouges, Widgets, Drawables, color optimization, and more!"
    # initialize the main dialouge
    mydialouge = AutoDialouge(width=WIDTH, ctype=ColorType.LEGACY)

    mydialouge.add_widget(WidgetLabel(
        title,
        size=Size(WIDTH),  # height will be owerwritten in WidgetLabel
        pos=Point(0, 1),
    ))

    mydialouge.add_widget(WidgetLabel(
        caption,
        centered=True,
        size=Size(WIDTH),  # height will be owerwritten in WidgetLabel
        pos=Point(0, 2),
    ))

    mydialouge.add_widget(WidgetInput(
        "text input: ",
        size=Size(WIDTH//2 - 4),  # height will be owerwritten in WidgetLabel
        pos=Point(2, 6),
    ))
    mydialouge.add_widget(WidgetInput(
        "another text input: ",
        size=Size(WIDTH//2 - 4),  # height will be owerwritten in WidgetLabel
        pos=Point(WIDTH//2 + 2, 6),
    ))

    
    # the text and callback function for each option
    options = [
        ("Nice!", nice_option),
        ("Very Cool!", verycool_option),
        ("Awesome!", awesome_option),
        ("Briliant!", briliant_option),
    ]
    mydialouge.add_widget(WidgetOptions(
        options,
        size=Size(WIDTH-4),  # height will be owerwritten in WidgetOptions
        pos=Point(2, 8),
    ))
    # the widgets are drawn in the order that they are added
    # so this text widget will be drawn on top of all ther widgets
    mydialouge.add_widget(WidgetLabel(
        CStr("Tip: ", forecolor=(220, 220, 0)) +
        CStr("you can use TAB or arrow keys to switch between selectable Widgets! and use ") + CStr("Ctrl + C", forecolor=(220, 220, 0)) +
        CStr(" or press enter on (InputWidget)s to exit!"),
        centered=True,
        size=Size(WIDTH - 24),  # height will be owerwritten in WidgetLabel
        pos=Point(22, 9),
    ))
    return mydialouge


if __name__ == "__main__":
    ansi.InitAnsi()

    mydialouge = main_dialouge()

    result = mydialouge.show()

    print(f"result (last callback return): \"{result}\"")

    print(f"individual outputs:")
    for i, w in enumerate(mydialouge.widgets):
        if isinstance(w, WidgetInput):
            print(f"text written in textbox ({w.text}): ", w.input)
        if isinstance(w, WidgetOptions):
            print("selected option id:", w.selected, "selected option text:", w.options[w.selected])

```