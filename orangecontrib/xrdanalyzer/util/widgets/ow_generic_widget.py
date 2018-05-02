import sys, numpy, os

from Orange.widgets import gui as orange_gui
from Orange.widgets import widget

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QDoubleValidator

from orangecontrib.xrdanalyzer.util.gui.gui_utility import ConfirmDialog, gui, ShowTextDialog

from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParameter, Boundary
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import PARAM_HWMAX, PARAM_HWMIN

class OWGenericWidget(widget.OWWidget):

    want_main_area=1

    is_automatic_run = Setting(True)

    error_id = 0
    warning_id = 0
    info_id = 0

    MAX_WIDTH = 1320
    MAX_WIDTH_NO_MAIN = 510
    MAX_HEIGHT = 700

    CONTROL_AREA_WIDTH = 505
    TABS_AREA_HEIGHT = 560

    fit_global_parameters = None
    parameter_functions = {}

    IS_DEVELOP = False if not "ORANGEDEVELOP" in os.environ.keys() else str(os.environ.get('ORANGEDEVELOP')) == "1"

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
            orange_gui.checkBox(self.general_options_box, self, 'is_automatic_run', 'Automatic')

        gui.button(self.general_options_box, self, "Reset Fields", callback=self.callResetSettings)

        gui.button(self.general_options_box, self, "Show Available Parameters", callback=self.show_available_parameters)


    def create_box(self, parent_box, var, label=None):
        box = gui.widgetBox(parent_box, "", orientation="horizontal", width=self.CONTROL_AREA_WIDTH - 50, height=25)

        box_label = gui.widgetBox(box, "", orientation="horizontal", width=40, height=25)
        box_value =  gui.widgetBox(box, "", orientation="horizontal", width=100, height=25)
        box_min_max = gui.widgetBox(box, "", orientation="horizontal", height=30)
        box_fixed = gui.widgetBox(box, "", orientation="horizontal", height=25)
        box_function = gui.widgetBox(box, "", orientation="horizontal", height=25)
        box_function_value = gui.widgetBox(box, "", orientation="horizontal", height=25)

        gui.widgetLabel(box_label, var if label is None else label)
        le_var = gui.lineEdit(box_value, self, var, "", valueType=float, validator=QDoubleValidator())

        def set_flags():
            fixed = getattr(self, var + "_fixed") == True
            function = getattr(self, var + "_function") == True

            if function:
                setattr(self, var + "_fixed", False)

                box_min_max.setVisible(False)
                box_fixed.setVisible(False)
                le_var.setVisible(False)
                box_value.setFixedWidth(5)
                box_function_value.setVisible(True)
            elif fixed:
                setattr(self, var + "_function", False)

                box_min_max.setVisible(False)
                le_var.setVisible(True)
                box_value.setFixedWidth(100)
                box_function.setVisible(False)
                box_function_value.setVisible(False)
            else:
                box_min_max.setVisible(True)
                le_var.setVisible(True)
                box_value.setFixedWidth(100)
                box_fixed.setVisible(True)
                box_function.setVisible(True)
                box_function_value.setVisible(False)

        self.parameter_functions[var] = set_flags

        orangegui.checkBox(box_fixed, self, var + "_fixed", "fix", callback=set_flags)

        orangegui.checkBox(box_min_max, self, var + "_has_min", "min")
        gui.lineEdit(box_min_max, self, var + "_min", "", valueType=float, validator=QDoubleValidator())
        orangegui.checkBox(box_min_max, self, var + "_has_max", "max")
        gui.lineEdit(box_min_max, self, var + "_max", "", valueType=float, validator=QDoubleValidator())

        orangegui.checkBox(box_function, self, var + "_function", "f(x)", callback=set_flags)
        gui.lineEdit(box_function_value, self, var + "_function_value", "expression", valueType=str)

        set_flags()

    def populate_parameter(self, parameter_name, parameter_prefix):
        if getattr(self, parameter_name + "_function") == 1:
            return FitParameter(parameter_name=parameter_prefix + parameter_name, function=True, function_value=getattr(self, parameter_name + "_function_value"))
        elif getattr(self, parameter_name + "_fixed") == 1:
            return FitParameter(parameter_name=parameter_prefix + parameter_name, value=getattr(self, parameter_name), fixed=True)
        else:
            boundary = None

            min_value = PARAM_HWMIN
            max_value = PARAM_HWMAX

            if getattr(self, parameter_name + "_has_min") == 1: min_value = getattr(self, parameter_name + "_min")
            if getattr(self, parameter_name + "_has_max") == 1: max_value = getattr(self, parameter_name + "_max")

            if min_value != PARAM_HWMIN or max_value != PARAM_HWMAX:
                boundary = Boundary(min_value=min_value, max_value=max_value)

            return FitParameter(parameter_name=parameter_prefix + parameter_name, value=getattr(self, parameter_name), boundary=boundary)

    def populate_fields(self, var, parameter, value_only=True):

        setattr(self, var, round(parameter.value, 8) if not parameter.value is None else 0.0)

        if not value_only:
            setattr(self, var + "_function", 1 if parameter.function else 0)
            setattr(self, var + "_function_value", parameter.function_value if parameter.function else "")
            setattr(self, var + "_fixed", 1 if parameter.fixed else 0)

            if not parameter.boundary is None:
                if parameter.boundary.min_value != PARAM_HWMIN:
                    setattr(self, var + "_has_min", 1)
                    setattr(self, var + "_min", round(parameter.boundary.min_value, 6))
                else:
                    setattr(self, var + "_has_min", 0)
                    setattr(self, var + "_min", 0.0)

                if parameter.boundary.max_value != PARAM_HWMAX:
                    setattr(self, var + "_has_max", 1)
                    setattr(self, var + "_max", round(parameter.boundary.max_value, 6))
                else:
                    setattr(self, var + "_has_max", 0)
                    setattr(self, var + "_max", 0.0)

            self.parameter_functions[var]()

    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self.resetSettings()
            except:
                pass

    def show_available_parameters(self):
        ShowTextDialog.show_text("Available Parameters", "" if self.fit_global_parameters is None else self.fit_global_parameters.get_available_parameters(), parent=self)