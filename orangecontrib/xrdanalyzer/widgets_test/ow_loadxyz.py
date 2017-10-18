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
from orangecontrib.xrdanalyzer.util.dlmethods.iomethods import loadxyz
import orangecontrib.xrdanalyzer.util.gui.congruence as congruence

class OWLoadxyz(OWGenericWidget):

    name = "Load xyz"
    description = "Loads an xyz file returning the element type and positions"
    icon = "icons/loadxyz.png"
    priority = 50

    want_main_area = True


    class Outputs:
       xyzdata = widget.Output("xyzdata", data.Table )

    def __init__(self):
        super().__init__(show_automatic_box=True)
        self.filename = None
        self.xyzdata = None
        orangegui.button(self.controlArea, self, "Open File...", callback=self.open_folders)
        #self.line = orangegui.lineEdit(self.controlArea, self, value="", valueType=data.FileFormat)
        self.label = orangegui.label(self, OWGenericWidget,str(self.filename))
        orangegui.button(self.controlArea, self, "Convert to Table", callback=self.loadxyz)

        self.text_area = self.textArea(height=600, width=700)

        self.layout().addWidget(self.text_area)
        button = gui.button(self.controlArea, self, "Show Data", width=200, height=50, callback=self.show_data)


    def open_folders(self):
        path=orangegui.QtWidgets.QFileDialog.getOpenFileName()
        self.label.setText(str(path[0]))
        self.filename = str(path[0])

    def loadxyz(self):
        element, x, y, z = loadxyz(self.filename)
        self.xyzdata = np.column_stack((element, x, y, z))

    def show_data(self):
        text = ""
        for row in self.xyzdata:
            text += "{}\t{}\t{}\t{}\n".format(str(row[0]), str(row[1]),#
                                              str(row[2]), str(row[3]) )
        #text = np.array_str(self.xyzdata)
        self.text_area.setText(text)

    def textArea(self, height=None, width=None, readOnly=True):
        area = QTextEdit()
        area.setReadOnly(readOnly)
        area.setStyleSheet("background-color: white;")

        if not height is None: area.setFixedHeight(height)
        if not width is None: area.setFixedWidth(width)

        return area




