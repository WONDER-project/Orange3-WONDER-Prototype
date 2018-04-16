import sys, numpy

from Orange.widgets import gui as orange_gui
from Orange.widgets import widget

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect

from orangecontrib.xrdanalyzer.util.gui.gui_utility import ConfirmDialog, gui

from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParameter, Boundary

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


    def create_box(self, parent_box, var):
        box = gui.widgetBox(parent_box, "", orientation="horizontal", width=self.CONTROL_AREA_WIDTH - 50)

        gui.lineEdit(box, self, var, var, labelWidth=20, valueType=float)
        orangegui.checkBox(box, self, var + "_fixed", "fix")
        orangegui.checkBox(box, self, var + "_has_min", "min")
        gui.lineEdit(box, self, var + "_min", "", labelWidth=5, valueType=float)
        orangegui.checkBox(box, self, var + "_has_max", "max")
        gui.lineEdit(box, self, var + "_max", "", labelWidth=5, valueType=float)


    def populate_parameter(self, parameter_name, parameter_prefix):
        if getattr(self, parameter_name + "_fixed") == 0:
            boundary = None

            min_value = -numpy.inf
            max_value = numpy.inf

            if getattr(self, parameter_name + "_has_min") == 1: min_value = getattr(self, parameter_name + "_min")
            if getattr(self, parameter_name + "_has_max") == 1: max_value = getattr(self, parameter_name + "_max")

            if min_value != -numpy.inf or max_value != numpy.inf:
                boundary = Boundary(min_value=min_value, max_value=max_value)

            return FitParameter(parameter_name=parameter_prefix + parameter_name, value=getattr(self, parameter_name), boundary=boundary)
        else:
            return FitParameter(parameter_name=parameter_prefix + parameter_name, value=getattr(self, parameter_name), fixed=True)



    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass
