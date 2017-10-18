from Orange.widgets import widget
from Orange.widgets.settings import Setting
from Orange.widgets import gui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui

class OWVisualizenum (OWGenericWidget):
    name = "Visualize Number"
    description = "Print out a number"
    icon = "icons/visualizenum.png"

    class Inputs:
        number = widget.Input("Number", int)

    def __init__(self):
        super().__init__(show_automatic_box=True)

        self.number = None
        self.label = gui.widgetLabel(self.controlArea, "The number is: ??")

    @Inputs.number
    def set_number(self, number):
        self.number = number
        if self.number is None:
            self.label.setText("The number is: ??")
        else:
            self.label.setText("The number is: {}".format(self.number))