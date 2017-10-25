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
from orangecontrib.xrdanalyzer.controller.fit.microstructure.strain import InvariantPAHLaueGroup14, LaueGroup

class OWStrain(OWGenericWidget):

    name = "Strain"
    description = "Define Strain"
    icon = "icons/strain.png"
    priority = 6

    want_main_area =  False

    laue_id = Setting(13)

    aa = Setting(0.0)
    bb = Setting(0.0)

    aa_fixed = Setting(0)
    bb_fixed = Setting(0)

    aa_has_min = Setting(0)
    bb_has_min = Setting(0)

    aa_min = Setting(0.0)
    bb_min = Setting(0.0)

    aa_has_max = Setting(0)
    bb_has_max = Setting(0)

    aa_max = Setting(0.0)
    bb_max = Setting(0.0)

    e1 = Setting(0.0)
    e6 = Setting(0.0)

    e1_fixed = Setting(0)
    e6_fixed = Setting(0)

    e1_has_min = Setting(0)
    e6_has_min = Setting(0)

    e1_min = Setting(0.0)
    e6_min = Setting(0.0)

    e1_has_max = Setting(0)
    e6_has_max = Setting(0)

    e1_max = Setting(0.0)
    e6_max = Setting(0.0)

    fit_global_parameters = None

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Size", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)

        self.create_box(main_box, "aa")
        self.create_box(main_box, "bb")


        invariant_box = gui.widgetBox(main_box,
                                 "Invariant Parameters", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 30)

        self.cb_laue_id = orangegui.comboBox(invariant_box, self, "laue_id", label="Laue Group", items=LaueGroup.tuple(), callback=self.set_laue_id, orientation="horizontal")

        self.create_box(invariant_box, "e1")
        self.create_box(invariant_box, "e6")

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Strain", height=50, callback=self.send_strain)

    def set_laue_id(self):
        if not self.laue_id == 13:
            QMessageBox.critical(self, "Error",
                                 "Only " + LaueGroup.get_laue_group(14) + " is supported",
                                 QMessageBox.Ok)

            self.laue_id = 13

    def send_strain(self):
        try:
            if not self.fit_global_parameters is None:
                self.fit_global_parameters.strain_parameters = InvariantPAHLaueGroup14(aa=self.populate_parameter("aa"),
                                                                                       bb=self.populate_parameter("bb"),
                                                                                       e1=self.populate_parameter("e1"),
                                                                                       e6=self.populate_parameter("e6"))

                #ShowTextDialog.show_text("Output", self.fit_global_parameters.strain_parameters.to_PM2K(), parent=self)

                #ShowTextDialog.show_text("FIT PARAMETERS", str(self.fit_global_parameters.to_scipy_tuple()[0]) + "\n\n" + str(self.fit_global_parameters.to_scipy_tuple()[1]), parent=self)


                self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            #raise e



    def set_data(self, data):
        self.fit_global_parameters = data

        if not self.fit_global_parameters is None and self.is_automatic_run:
            self.send_strain()





if __name__ == "__main__":
    a4 =  QApplication(sys.argv)
    ow = OWDiffractionPattern()
    ow.show()
    a.exec_()
    ow.saveSettings()
