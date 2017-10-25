import sys

from Orange.widgets import gui as orange_gui
from Orange.widgets import widget

from Orange.widgets.settings import Setting

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect

from orangecontrib.xrdanalyzer.util.gui.gui_utility import ConfirmDialog, gui

class OWGenericWidget(widget.OWWidget):

    want_main_area=1

    is_automatic_run = Setting(True)

    error_id = 0
    warning_id = 0
    info_id = 0

    MAX_WIDTH = 1320
    MAX_WIDTH_NO_MAIN = 410
    MAX_HEIGHT = 700

    CONTROL_AREA_WIDTH = 405
    TABS_AREA_HEIGHT = 560

    def __init__(self, show_automatic_box=True):
        super().__init__()

        geom = QApplication.desktop().availableGeometry()

        if self.want_main_area:
            max_width = self.MAX_WIDTH
        else:
            max_width = self.MAX_WIDTH_NO_MAIN

        self.setGeometry(QRect(round(geom.width()*0.05),
                               round(geom.height()*0.05),
                               round(min(geom.width()*0.98, max_width)),
                               round(min(geom.height()*0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        self.general_options_box = gui.widgetBox(self.controlArea, "General Options", addSpace=True, orientation="horizontal")

        if show_automatic_box :
            orange_gui.checkBox(self.general_options_box, self, 'is_automatic_run', 'Automatic Execution')

        gui.button(self.general_options_box, self, "Reset Fields", callback=self.callResetSettings)


    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass
