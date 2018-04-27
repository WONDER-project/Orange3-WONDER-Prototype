import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget, QApplication


from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui, ShowTextDialog
from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.instrument.instrumental_parameters import Caglioti, Lab6TanCorrection

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

    U_function = Setting(0)
    V_function = Setting(0)
    W_function = Setting(0)

    U_function_value = Setting("")
    V_function_value = Setting("")
    W_function_value = Setting("")

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

    a_function = Setting(0)
    b_function = Setting(0)
    c_function = Setting(0)

    a_function_value = Setting("")
    b_function_value = Setting("")
    c_function_value = Setting("")

    #########################################
    
    ax = Setting(0.0)
    bx = Setting(0.0)
    cx = Setting(0.0)
    dx = Setting(0.0)
    ex = Setting(0.0)

    ax_fixed = Setting(0)
    bx_fixed = Setting(0)
    cx_fixed = Setting(0)
    dx_fixed = Setting(0)
    ex_fixed = Setting(0)

    ax_has_min = Setting(0)
    bx_has_min = Setting(0)
    cx_has_min = Setting(0)
    dx_has_min = Setting(0)
    ex_has_min = Setting(0)

    ax_min = Setting(0.0)
    bx_min = Setting(0.0)
    cx_min = Setting(0.0)
    dx_min = Setting(0.0)
    ex_min = Setting(0.0)

    ax_has_max = Setting(0)
    bx_has_max = Setting(0)
    cx_has_max = Setting(0)
    dx_has_max = Setting(0)
    ex_has_max = Setting(0)

    ax_max = Setting(0.0)
    bx_max = Setting(0.0)
    cx_max = Setting(0.0)
    dx_max = Setting(0.0)
    ex_max = Setting(0.0)

    ax_function = Setting(0)
    bx_function = Setting(0)
    cx_function = Setting(0)
    dx_function = Setting(0)
    ex_function = Setting(0)

    ax_function_value = Setting("")
    bx_function_value = Setting("")
    cx_function_value = Setting("")
    dx_function_value = Setting("")
    ex_function_value = Setting("")

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

        self.create_box(lab6_box, "ax")
        self.create_box(lab6_box, "bx")
        self.create_box(lab6_box, "cx")
        self.create_box(lab6_box, "dx")
        self.create_box(lab6_box, "ex")

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Instrumental Profile", height=50, callback=self.send_intrumental_profile)


    def send_intrumental_profile(self):
        try:
            if not self.fit_global_parameters is None:

                self.fit_global_parameters.instrumental_parameters = Caglioti(U=self.populate_parameter("U", Caglioti.get_parameters_prefix()),
                                                                              V=self.populate_parameter("V", Caglioti.get_parameters_prefix()),
                                                                              W=self.populate_parameter("W", Caglioti.get_parameters_prefix()),
                                                                              a=self.populate_parameter("a", Caglioti.get_parameters_prefix()),
                                                                              b=self.populate_parameter("b", Caglioti.get_parameters_prefix()),
                                                                              c=self.populate_parameter("c", Caglioti.get_parameters_prefix()))

                self.fit_global_parameters.lab6_tan_correction = Lab6TanCorrection(ax=self.populate_parameter("ax", Lab6TanCorrection.get_parameters_prefix()),
                                                                                   bx=self.populate_parameter("bx", Lab6TanCorrection.get_parameters_prefix()),
                                                                                   cx=self.populate_parameter("cx", Lab6TanCorrection.get_parameters_prefix()),
                                                                                   dx=self.populate_parameter("dx", Lab6TanCorrection.get_parameters_prefix()),
                                                                                   ex=self.populate_parameter("ex", Lab6TanCorrection.get_parameters_prefix()))

                self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            #raise e


    def set_data(self, data):
        if not data is None:
            self.fit_global_parameters = data.duplicate()

            if not self.fit_global_parameters.instrumental_parameters is None:
                self.U = self.fit_global_parameters.instrumental_parameters.U.value
                self.V = self.fit_global_parameters.instrumental_parameters.V.value
                self.W = self.fit_global_parameters.instrumental_parameters.W.value
                self.a = self.fit_global_parameters.instrumental_parameters.a.value
                self.b = self.fit_global_parameters.instrumental_parameters.b.value
                self.c = self.fit_global_parameters.instrumental_parameters.c.value

            if not self.fit_global_parameters.lab6_tan_correction is None:
                self.ax = self.fit_global_parameters.lab6_tan_correction.ax.value
                self.bx = self.fit_global_parameters.lab6_tan_correction.bx.value
                self.cx = self.fit_global_parameters.lab6_tan_correction.cx.value
                self.dx = self.fit_global_parameters.lab6_tan_correction.dx.value
                self.ex = self.fit_global_parameters.lab6_tan_correction.ex.value

            if self.is_automatic_run:
                self.send_intrumental_profile()



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWInstrumentalProfile()
    ow.show()
    a.exec_()
    ow.saveSettings()
