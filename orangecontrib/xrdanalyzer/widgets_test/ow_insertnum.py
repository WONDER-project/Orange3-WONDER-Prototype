from Orange.widgets import widget
from Orange.widgets.settings import Setting
from Orange.widgets import gui

from PyQt5.QtGui import QIntValidator

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget

class OWInsertnum(OWGenericWidget):
    name = "Integer Number"

    description = "Let's the user input a number"

    icon = "icons/number.png"

    priority = 1

    number = Setting(42)

    class Outputs:
        number = widget.Output("Number", int)

    def __init__ (self):
        super().__init__()

        gui.lineEdit(self.controlArea, self, "number", "Enter a number",
                     box="Number", callback=self.number_changed,
                     valueType=int, validator=QIntValidator() )
        self.number_changed()
    def number_changed(self):
        #send entered number on "Number" output
        self.Outputs.number.send(self.number)