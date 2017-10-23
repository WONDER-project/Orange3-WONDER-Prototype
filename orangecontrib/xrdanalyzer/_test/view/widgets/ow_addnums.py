from Orange.widgets import widget
from Orange.widgets.settings import Setting
from Orange.widgets import gui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui

class OWAddnums(OWGenericWidget):
    name = "Add Numbers"
    description = "Sums two integers"
    icon = "icons/addnums.png"
    priority = 2

    class Inputs:
        a = widget.Input("A", int)
        b = widget.Input("B", int)

    class Outputs:
        sum = widget.Output("A+B", int)

    def __init__(self):
        super().__init__(show_automatic_box=True)
        self.a = None
        self.b = None

    @Inputs.a
    def set_A(self, a):
        self.a = a

    @Inputs.b
    def set_B(self, b):
        self.b = b

    def handleNewSignals(self):
        if self.a is not None and self.b is not None:
            self.Outputs.sum.send(self.a + self.b)
        else:
            self.Outputs.sum.send(None)