import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget, QApplication
from PyQt5.QtCore import Qt

from silx.gui.plot.PlotWindow import PlotWindow

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui, ShowTextDialog
from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPatternFactory

from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParameter, Boundary
from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.init.fit_initialization import FitInitialization
from orangecontrib.xrdanalyzer.controller.fit.microstructure.size import SizeParameters, Shape, Distribution

class OWSize(OWGenericWidget):

    name = "Size"
    description = "Define Size"
    icon = "icons/size.png"
    priority = 10

    want_main_area =  False

    shape = Setting(1)
    distribution = Setting(1)

    mu = Setting(4.0)
    sigma = Setting(0.5)

    mu_fixed = Setting(0)
    sigma_fixed = Setting(0)

    mu_has_min = Setting(1)
    sigma_has_min = Setting(1)

    mu_min = Setting(0.01)
    sigma_min = Setting(0.01)

    mu_has_max = Setting(0)
    sigma_has_max = Setting(1)

    mu_max = Setting(0.0)
    sigma_max = Setting(1.0)

    mu_function = Setting(0)
    sigma_function = Setting(0)

    mu_function_value = Setting("")
    sigma_function_value = Setting("")

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Size", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)

        self.cb_shape = orangegui.comboBox(main_box, self, "shape", label="Shape", items=Shape.tuple(), callback=self.set_shape, orientation="horizontal")
        self.cb_distribution = orangegui.comboBox(main_box, self, "distribution", label="Distribution", items=Distribution.tuple(), callback=self.set_distribution, orientation="horizontal")


        size_box = gui.widgetBox(main_box,
                                 "Size Parameters", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 30)
        
        
        
        self.create_box(size_box, "mu")
        self.create_box(size_box, "sigma")

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Size", height=50, callback=self.send_size)

    def set_shape(self):
        if not self.cb_shape.currentText() == Shape.SPHERE:
            QMessageBox.critical(self, "Error",
                                 "Only Sphere shape is supported",
                                 QMessageBox.Ok)

            self.shape = 1

    def set_distribution(self):
        if not self.cb_distribution.currentText() == Distribution.LOGNORMAL:
            QMessageBox.critical(self, "Error",
                                 "Only Lognormal distribution is supported",
                                 QMessageBox.Ok)

            self.distribution = 1

    def send_size(self):
        try:
            if not self.fit_global_parameters is None:
                self.fit_global_parameters.size_parameters = [SizeParameters(shape=self.cb_shape.currentText(),
                                                                            distribution=self.cb_distribution.currentText(),
                                                                            mu=self.populate_parameter("mu", SizeParameters.get_parameters_prefix()),
                                                                            sigma=self.populate_parameter("sigma", SizeParameters.get_parameters_prefix()))]

                self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e



    def set_data(self, data):
        if not data is None:
            self.fit_global_parameters = data.duplicate()

            if not self.fit_global_parameters.size_parameters is None:
                self.populate_fields("mu",    self.fit_global_parameters.size_parameters[0].mu)
                self.populate_fields("sigma", self.fit_global_parameters.size_parameters[0].sigma)

            if self.is_automatic_run:
                self.send_size()





if __name__ == "__main__":
    a =  QApplication(sys.argv)
    ow = OWSize()
    ow.show()
    a.exec_()
    ow.saveSettings()
