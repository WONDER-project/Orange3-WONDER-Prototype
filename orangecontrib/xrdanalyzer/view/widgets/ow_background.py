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
from orangecontrib.xrdanalyzer.controller.fit.instrument.background_parameters import ChebyshevBackground

class OWBackground(OWGenericWidget):

    name = "Background"
    description = "Define background"
    icon = "icons/background.png"
    priority = 4

    want_main_area =  False

    a0 = Setting(0.0)
    a1 = Setting(0.0)
    a2 = Setting(0.0)

    a0_fixed = Setting(0)
    a1_fixed = Setting(0)
    a2_fixed = Setting(0)

    a0_has_min = Setting(0)
    a1_has_min = Setting(0)
    a2_has_min = Setting(0)

    a0_min = Setting(0.0)
    a1_min = Setting(0.0)
    a2_min = Setting(0.0)

    a0_has_max = Setting(0)
    a1_has_max = Setting(0)
    a2_has_max = Setting(0)

    a0_max = Setting(0.0)
    a1_max = Setting(0.0)
    a2_max = Setting(0.0)

    a3 =  Setting(0.0)
    a4 =  Setting(0.0)
    a5 =  Setting(0.0)

    a3_fixed = Setting(0)
    a4_fixed = Setting(0)
    a5_fixed = Setting(0)

    a3_has_min = Setting(0)
    a4_has_min = Setting(0)
    a5_has_min = Setting(0)

    a3_min = Setting(0.0)
    a4_min = Setting(0.0)
    a5_min = Setting(0.0)

    a3_has_max = Setting(0)
    a4_has_max = Setting(0)
    a5_has_max = Setting(0)

    a3_max = Setting(0.0)
    a4_max = Setting(0.0)
    a5_max = Setting(0.0)

    fit_global_parameters = None

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Instrumental Profile", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)


        chebyshev_box = gui.widgetBox(main_box,
                                 "Chebyshev Parameters", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 30)

        self.create_box(chebyshev_box, "a0")
        self.create_box(chebyshev_box, "a1")
        self.create_box(chebyshev_box, "a2")
        self.create_box(chebyshev_box, "a3")
        self.create_box(chebyshev_box, "a4")
        self.create_box(chebyshev_box, "a5")

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Background", height=50, callback=self.send_background)


    def send_background(self):
        try:
            if not self.fit_global_parameters is None:

                self.fit_global_parameters.background_parameters = ChebyshevBackground(c0=self.populate_parameter("a0"),
                                                                                       c1=self.populate_parameter("a1"),
                                                                                       c2=self.populate_parameter("a2"),
                                                                                       c3=self.populate_parameter("a3"),
                                                                                       c4=self.populate_parameter("a4"),
                                                                                       c5=self.populate_parameter("a5"))

                #ShowTextDialog.show_text("Output", self.fit_global_parameters.background_parameters.to_PM2K(), parent=self)

                self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            #raise e


    def set_data(self, data):
        if not data is None:
            self.fit_global_parameters = data.duplicate()

            if self.is_automatic_run:
                self.send_background()



if __name__ == "__main__":
    a4 =  QApplication(sys.argv)
    ow = OWDiffractionPattern()
    ow.show()
    a.exec_()
    ow.saveSettings()
