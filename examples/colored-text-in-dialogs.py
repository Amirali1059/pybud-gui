# import the main dialog class
from pybud.gui.dialog import AutoDialog
# import widgets
from pybud.gui.widgets import WidgetLabel
# import `ColoredString` (using this class you can define text with color)
from pybud.drawer.ansi import AnsiString as AStr

# build the main dialog, set width and background color
d = AutoDialog(width=60, background_color=(90, 90, 250))
# add a label widget, set text, width and position
d.add_widget(WidgetLabel(
    # define a ColoredString object that renders text with colors
    # you can set both forecolor and backcolor
    text=AStr("Hello world!", fore = (90, 250, 90)),
    pos=[0, 1],
    size=[60, None]
    )
)
# show the dialog
d.show()
# after the dialog closes
print("closed!")