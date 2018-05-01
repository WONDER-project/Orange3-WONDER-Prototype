import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget, QApplication


from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui, ShowTextDialog
from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.instrument.background_parameters import ChebyshevBackground

class OWBackground(OWGenericWidget):

    name = "Background"
    description = "Define background"
    icon = "icons/background.png"
    priority = 4

    want_main_area =  False

    c0 = Setting(0.0)
    c1 = Setting(0.0)
    c2 = Setting(0.0)
    c3 =  Setting(0.0)
    c4 =  Setting(0.0)
    c5 =  Setting(0.0)

    c0_fixed = Setting(0)
    c1_fixed = Setting(0)
    c2_fixed = Setting(0)
    c3_fixed = Setting(0)
    c4_fixed = Setting(0)
    c5_fixed = Setting(0)

    c0_has_min = Setting(0)
    c1_has_min = Setting(0)
    c2_has_min = Setting(0)
    c3_has_min = Setting(0)
    c4_has_min = Setting(0)
    c5_has_min = Setting(0)

    c0_min = Setting(0.0)
    c1_min = Setting(0.0)
    c2_min = Setting(0.0)
    c3_min = Setting(0.0)
    c4_min = Setting(0.0)
    c5_min = Setting(0.0)

    c0_has_max = Setting(0)
    c1_has_max = Setting(0)
    c2_has_max = Setting(0)
    c3_has_max = Setting(0)
    c4_has_max = Setting(0)
    c5_has_max = Setting(0)

    c0_max = Setting(0.0)
    c1_max = Setting(0.0)
    c2_max = Setting(0.0)
    c3_max = Setting(0.0)
    c4_max = Setting(0.0)
    c5_max = Setting(0.0)

    c0_function = Setting(0)
    c1_function = Setting(0)
    c2_function = Setting(0)
    c3_function = Setting(0)
    c4_function = Setting(0)
    c5_function = Setting(0)

    c0_function_value = Setting("")
    c1_function_value = Setting("")
    c2_function_value = Setting("")
    c3_function_value = Setting("")
    c4_function_value = Setting("")
    c5_function_value = Setting("")

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

        self.create_box(chebyshev_box, "c0")
        self.create_box(chebyshev_box, "c1")
        self.create_box(chebyshev_box, "c2")
        self.create_box(chebyshev_box, "c3")
        self.create_box(chebyshev_box, "c4")
        self.create_box(chebyshev_box, "c5")

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Background", height=50, callback=self.send_background)


    def send_background(self):
        try:
            if not self.fit_global_parameters is None:
                self.fit_global_parameters.background_parameters = ChebyshevBackground(c0=self.populate_parameter("c0", ChebyshevBackground.get_parameters_prefix()),
                                                                                       c1=self.populate_parameter("c1", ChebyshevBackground.get_parameters_prefix()),
                                                                                       c2=self.populate_parameter("c2", ChebyshevBackground.get_parameters_prefix()),
                                                                                       c3=self.populate_parameter("c3", ChebyshevBackground.get_parameters_prefix()),
                                                                                       c4=self.populate_parameter("c4", ChebyshevBackground.get_parameters_prefix()),
                                                                                       c5=self.populate_parameter("c5", ChebyshevBackground.get_parameters_prefix()))

                self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e


    def set_data(self, data):
        if not data is None:
            self.fit_global_parameters = data.duplicate()

            if not self.fit_global_parameters.background_parameters is None:
                self.c0 = self.fit_global_parameters.background_parameters.c0.value
                self.c1 = self.fit_global_parameters.background_parameters.c1.value
                self.c2 = self.fit_global_parameters.background_parameters.c2.value
                self.c3 = self.fit_global_parameters.background_parameters.c3.value
                self.c4 = self.fit_global_parameters.background_parameters.c4.value
                self.c5 = self.fit_global_parameters.background_parameters.c5.value

            if self.is_automatic_run:
                self.send_background()



if __name__ == "__main__":
    a4 =  QApplication(sys.argv)
    ow = OWBackground()
    ow.show()
    a.exec_()
    ow.saveSettings()
