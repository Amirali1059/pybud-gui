# import the main dialog class
from pybud.gui.dialog import AutoDialog
# import widgets
from pybud.gui.widgets import WidgetLabel
# import `ColoredString` (using this class you can define text with color)
from pybud.drawing import ColoredString as CStr
# import types
from pybud.deftypes import Point, Size

# build the main dialog, set width and background color
d = AutoDialog(width=60, background_color=(90, 90, 250))
# add a label widget, set text, width and position
d.add_widget(WidgetLabel(
    # define a ColoredString object that renders text with colors
    # you can set both forecolor and backcolor
    text=CStr("Hello world!", forecolor=(90, 250, 90)),
    pos=Point(y=1),
    size=Size(w=60)
    )
)
# show the dialog
d.show()
# after the dialog closes
print("closed!")