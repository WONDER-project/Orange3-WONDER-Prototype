from Orange.widgets import widget
from Orange.widgets.settings import Setting
from Orange.widgets import gui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui

class OWVisualizenum (OWGenericWidget):
    name = "Visualize Number"
    description = "Print out a number"
    icon = "icons/visualizenum.png"
    priority = 3


    def __init__(self):
        super().__init__(show_automatic_box=True)

