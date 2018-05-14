import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget, QApplication


from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui, ShowTextDialog
from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.instrument.background_parameters import ChebyshevBackground

class OWChebyshevBackground(OWGenericWidget):

    name = "Chebyshev Background"
    description = "Define Chebyshev background"
    icon = "icons/chebyshev_background.png"
    priority = 5

    want_main_area =  False

    c0 = Setting(0.0)
    c1 = Setting(0.0)
    c2 = Setting(0.0)
    c3 =  Setting(0.0)
    c4 =  Setting(0.0)
    c5 =  Setting(0.0)
    c6 = Setting(0.0)
    c7 =  Setting(0.0)
    c8 =  Setting(0.0)
    c9 =  Setting(0.0)

    c0_fixed = Setting(0)
    c1_fixed = Setting(0)
    c2_fixed = Setting(0)
    c3_fixed = Setting(0)
    c4_fixed = Setting(0)
    c5_fixed = Setting(0)
    c6_fixed = Setting(1)
    c7_fixed = Setting(1)
    c8_fixed = Setting(1)
    c9_fixed = Setting(1)

    c0_has_min = Setting(0)
    c1_has_min = Setting(0)
    c2_has_min = Setting(0)
    c3_has_min = Setting(0)
    c4_has_min = Setting(0)
    c5_has_min = Setting(0)
    c6_has_min = Setting(0)
    c7_has_min = Setting(0)
    c8_has_min = Setting(0)
    c9_has_min = Setting(0)

    c0_min = Setting(0.0)
    c1_min = Setting(0.0)
    c2_min = Setting(0.0)
    c3_min = Setting(0.0)
    c4_min = Setting(0.0)
    c5_min = Setting(0.0)
    c6_min = Setting(0.0)
    c7_min = Setting(0.0)
    c8_min = Setting(0.0)
    c9_min = Setting(0.0)

    c0_has_max = Setting(0)
    c1_has_max = Setting(0)
    c2_has_max = Setting(0)
    c3_has_max = Setting(0)
    c4_has_max = Setting(0)
    c5_has_max = Setting(0)
    c6_has_max = Setting(0)
    c7_has_max = Setting(0)
    c8_has_max = Setting(0)
    c9_has_max = Setting(0)

    c0_max = Setting(0.0)
    c1_max = Setting(0.0)
    c2_max = Setting(0.0)
    c3_max = Setting(0.0)
    c4_max = Setting(0.0)
    c5_max = Setting(0.0)
    c6_max = Setting(0.0)
    c7_max = Setting(0.0)
    c8_max = Setting(0.0)
    c9_max = Setting(0.0)

    c0_function = Setting(0)
    c1_function = Setting(0)
    c2_function = Setting(0)
    c3_function = Setting(0)
    c4_function = Setting(0)
    c5_function = Setting(0)
    c6_function = Setting(0)
    c7_function = Setting(0)
    c8_function = Setting(0)
    c9_function = Setting(0)

    c0_function_value = Setting("")
    c1_function_value = Setting("")
    c2_function_value = Setting("")
    c3_function_value = Setting("")
    c4_function_value = Setting("")
    c5_function_value = Setting("")
    c6_function_value = Setting("")
    c7_function_value = Setting("")
    c8_function_value = Setting("")
    c9_function_value = Setting("")

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
        self.create_box(chebyshev_box, "c6")
        self.create_box(chebyshev_box, "c7")
        self.create_box(chebyshev_box, "c8")
        self.create_box(chebyshev_box, "c9")

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Background", height=50, callback=self.send_background)


    def send_background(self):
        try:
            if not self.fit_global_parameters is None:
                self.fit_global_parameters.set_background_parameters(ChebyshevBackground(c0=self.populate_parameter("c0", ChebyshevBackground.get_parameters_prefix()),
                                                                                         c1=self.populate_parameter("c1", ChebyshevBackground.get_parameters_prefix()),
                                                                                         c2=self.populate_parameter("c2", ChebyshevBackground.get_parameters_prefix()),
                                                                                         c3=self.populate_parameter("c3", ChebyshevBackground.get_parameters_prefix()),
                                                                                         c4=self.populate_parameter("c4", ChebyshevBackground.get_parameters_prefix()),
                                                                                         c5=self.populate_parameter("c5", ChebyshevBackground.get_parameters_prefix()),
                                                                                         c6=self.populate_parameter("c6", ChebyshevBackground.get_parameters_prefix()),
                                                                                         c7=self.populate_parameter("c7", ChebyshevBackground.get_parameters_prefix()),
                                                                                         c8=self.populate_parameter("c8", ChebyshevBackground.get_parameters_prefix()),
                                                                                         c9=self.populate_parameter("c9", ChebyshevBackground.get_parameters_prefix())))

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
                background_parameters = self.fit_global_parameters.get_background_parameters(ChebyshevBackground.__name__)

                if not background_parameters is None:
                    self.populate_fields("c0", background_parameters.c0)
                    self.populate_fields("c1", background_parameters.c1)
                    self.populate_fields("c2", background_parameters.c2)
                    self.populate_fields("c3", background_parameters.c3)
                    self.populate_fields("c4", background_parameters.c4)
                    self.populate_fields("c5", background_parameters.c5)
                    self.populate_fields("c6", background_parameters.c6)
                    self.populate_fields("c7", background_parameters.c7)
                    self.populate_fields("c8", background_parameters.c8)
                    self.populate_fields("c9", background_parameters.c9)

            if self.is_automatic_run:
                self.send_background()



if __name__ == "__main__":
    a4 =  QApplication(sys.argv)
    ow = OWChebyshevBackground()
    ow.show()
    a.exec_()
    ow.saveSettings()
