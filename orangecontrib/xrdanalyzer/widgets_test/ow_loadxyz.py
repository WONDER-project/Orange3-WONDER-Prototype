from Orange.widgets import widget
from Orange.widgets.settings import Setting
import Orange.widgets.gui as orangegui
from Orange import data
from Orange.widgets.utils import filedialogs
import os
from Orange.data.io import FileFormat
import numpy as np

from PyQt5.QtWidgets import QMessageBox, QTextEdit




from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui
from orangecontrib.xrdanalyzer.util.dlmethods.iomethods import loadxyz_multiple_arrays, loadxyz_numpy
import orangecontrib.xrdanalyzer.util.gui.congruence as congruence

class OWLoadxyz(OWGenericWidget):

    name = "Load xyz"
    description = "Loads an xyz file returning the element type and positions"
    icon = "icons/loadxyz.png"
    priority = 50

    want_main_area = True

    filename = Setting("<input file>")
    xyzdata = None

    outputs = [("Data", data.Table)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea, "Load xyz file",orientation="vertical", width=self.CONTROL_AREA_WIDTH-5, height=600)

        file_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        self.le_filename = gui.lineEdit(file_box,
                                        self,
                                        value="filename",
                                        valueType=str,
                                        label="File",
                                        labelWidth=50)

        orangegui.button(file_box, self, "...", width=40, callback=self.open_folders)

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Convert to Table", width=185, height=50, callback=self.loadxyz)
        gui.button(button_box,  self, "Show Data", width=185, height=50, callback=self.show_data)

        show_box = gui.widgetBox(self.mainArea, "the file is:", orientation="vertical")

        self.text_area = gui.textArea(height=600, width=700)
        show_box.layout().addWidget(self.text_area)

    def open_folders(self):
        self.filename=gui.selectFileFromDialog(self,
                                               self.filename,
                                               start_directory=os.curdir,
                                               file_extension_filter="*.xyz")

        self.le_filename.setText(self.filename)

    def loadxyz(self):
        try:
            congruence.checkFile(self.filename)

            element, x, y, z = loadxyz_multiple_arrays(self.filename)
            self.xyzdata = np.column_stack((element, x, y, z))
        except Exception as e:
            QMessageBox.critical(self, "Input Error",
                                 str(e),
                                 QMessageBox.Ok)


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


import sys
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWLoadxyz()
    ow.show()
    a.exec_()
    ow.saveSettings()


