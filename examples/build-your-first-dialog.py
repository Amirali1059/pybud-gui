# import the main dialog class
from pybud.gui.dialog import AutoDialog
# import widgets
from pybud.gui.widgets import WidgetLabel
# import types
from pybud.deftypes import Point, Size

# build the main dialog, set width and background color
d = AutoDialog(width=60, background_color=(90, 90, 250))
# add the main widget, set text, width and position
d.add_widget(WidgetLabel("Hello world!", pos=Point(y=1), size=Size(w=60)))
# show the dialog
d.show()
# after the dialog closes
print("closed!")