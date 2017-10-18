import sys
import numpy

import Orange.data
from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from Orange.widgets.widget import Input,  Output
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui

class OWDataSamplerA(OWGenericWidget):
    name = "Data Sampler"
    description = "Randomly selects a subset of instances from data set"
    icon = "icons/datasampler.png"

    priority = 10