import numpy

from Orange.widgets import gui as orange_gui
from Orange.widgets.settings import Setting
from Orange.data import Table

from PyQt5.QtWidgets import QApplication, QTextEdit, QMessageBox
from PyQt5.QtCore import QRect, Qt

from silx.gui.plot.PlotWindow import PlotWindow

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui, ShowTextDialog

class OWProva2(OWGenericWidget):
    name = "Prova 2"
    description = "Fazo na prova naltra olta"
    icon = "icons/prova.png"
    priority = 2

    inputs = [("XRD Data", Table, 'set_data')]
    outputs = [("Data", Table)]

    input_data = None

    want_main_area = True

    def __init__(self):
        super().__init__(show_automatic_box=True)

    def set_data(self, data):
        ShowTextDialog.show_text("ZIO TRENO", "GO CIAPA' DI DATTTI", parent=self)

        if self.is_automatic_run:
            self.send("Data", data)