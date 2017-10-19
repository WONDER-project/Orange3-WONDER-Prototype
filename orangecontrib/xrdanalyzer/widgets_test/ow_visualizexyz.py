from Orange.widgets import widget
from Orange.widgets.settings import Setting
import Orange.widgets.gui as orangegui
from Orange import data
from Orange.widgets.utils import filedialogs
import os
from Orange.data.io import FileFormat
import numpy as np

from PyQt5.QtWidgets import  QTextEdit




from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui
from orangecontrib.xrdanalyzer.util.dlmethods.iomethods import loadxyz2
import orangecontrib.xrdanalyzer.util.gui.congruence as congruence

class OWVisualizexyz(OWGenericWidget):

    name = "Visualize xyz"
    description = "Visualize the result of loading an xyz file"
    icon = "icons/visualizexyz.png"
    priority = 51

    want_main_area = True


    #class Inputs:
    #   xyzdata = widget.Output("xyzdata", data.Table )
    def __init__(self):
        super().__init__(show_automatic_box=True)
        #self.filename = None
        self.xyzdata = None
