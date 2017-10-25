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
from orangecontrib.xrdanalyzer.controller.fit.instrument.instrumental_parameters import Caglioti

class OWInstrumentalProfile(OWGenericWidget):

    name = "Instrumental Profile"
    description = "Define Instrumental Profile Parameters"
    icon = "icons/instrumental_profile.png"
    priority = 3

    want_main_area = False

    U = Setting(0.0)
    V = Setting(0.0)
    W = Setting(0.0)

    U_fixed = Setting(0)
    V_fixed = Setting(0)
    W_fixed = Setting(0)

    U_has_min = Setting(0)
    V_has_min = Setting(0)
    W_has_min = Setting(0)

    U_min = Setting(0.0)
    V_min = Setting(0.0)
    W_min = Setting(0.0)

    U_has_max = Setting(0)
    V_has_max = Setting(0)
    W_has_max = Setting(0)

    U_max = Setting(0.0)
    V_max = Setting(0.0)
    W_max = Setting(0.0)


    a = Setting(0.0)
    b = Setting(0.0)
    c = Setting(0.0)

    a_fixed = Setting(0)
    b_fixed = Setting(0)
    c_fixed = Setting(0)

    a_has_min = Setting(0)
    b_has_min = Setting(0)
    c_has_min = Setting(0)

    a_min = Setting(0.0)
    b_min = Setting(0.0)
    c_min = Setting(0.0)

    a_has_max = Setting(0)
    b_has_max = Setting(0)
    c_has_max = Setting(0)

    a_max = Setting(0.0)
    b_max = Setting(0.0)
    c_max = Setting(0.0)


    fit_global_parameters = None

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Instrumental Profile", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)


        caglioti_box_1 = gui.widgetBox(main_box,
                                 "Caglioti FWHM", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 30)
        
        caglioti_box_2 = gui.widgetBox(main_box,
                                 "Caglioti ETA", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 30)

        self.create_box(caglioti_box_1, "U")
        self.create_box(caglioti_box_1, "V")
        self.create_box(caglioti_box_1, "W")
        self.create_box(caglioti_box_2, "a")
        self.create_box(caglioti_box_2, "b")
        self.create_box(caglioti_box_2, "c")

        lab6_box = gui.widgetBox(main_box,
                                    "Lab6 Tan Correction", orientation="vertical",
                                    width=self.CONTROL_AREA_WIDTH - 30)

        orangegui.label(lab6_box, self, "TO BE DONE")

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Instrumental Profile", height=50, callback=self.send_intrumental_profile)


    def send_intrumental_profile(self):
        try:
            if not self.fit_global_parameters is None:

                self.fit_global_parameters.instrumental_parameters = Caglioti(U=self.populate_parameter("U"),
                                                                              V=self.populate_parameter("V"),
                                                                              W=self.populate_parameter("W"),
                                                                              a=self.populate_parameter("a"),
                                                                              b=self.populate_parameter("b"),
                                                                              c=self.populate_parameter("c"))

                ShowTextDialog.show_text("Output", self.fit_global_parameters.instrumental_parameters.to_PM2K(), parent=self)

                self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            raise e


    def set_data(self, data):
        self.fit_global_parameters = data

        if not self.fit_global_parameters is None and self.is_automatic_run:
            self.send_intrumental_profile()





if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWDiffractionPattern()
    ow.show()
    a.exec_()
    ow.saveSettings()
