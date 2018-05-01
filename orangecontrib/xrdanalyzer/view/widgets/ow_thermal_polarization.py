import sys

from PyQt5.QtWidgets import QMessageBox, QApplication

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import ConfirmDialog, gui
from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.init.thermal_polarization_parameters import ThermalPolarizationParameters

class OWThermalPolarization(OWGenericWidget):

    name = "Thermal and Polarization Factors"
    description = "Define Thermal and Polarization Factors"
    icon = "icons/thermal_polarization.png"
    priority = 4

    want_main_area = False

    use_debye_waller_factor = Setting(1)

    debye_waller_factor = Setting(0.0)
    debye_waller_factor_fixed = Setting(0)
    debye_waller_factor_has_min = Setting(0)
    debye_waller_factor_min = Setting(0.0)
    debye_waller_factor_has_max = Setting(0)
    debye_waller_factor_max = Setting(0.0)
    debye_waller_factor_function = Setting(0)
    debye_waller_factor_function_value = Setting("")

    use_lorentz_polarization_factor = Setting(1)

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Thermal and Polarization Factors", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=300)


        box = gui.widgetBox(main_box,
                            "Debye-Waller Factor", orientation="vertical",
                            width=self.CONTROL_AREA_WIDTH - 30)

        orangegui.comboBox(box, self, "use_debye_waller_factor", label="Calculate", items=["No", "Yes"], labelWidth=250, orientation="horizontal", callback=self.set_dw)

        self.box_dw       = gui.widgetBox(box, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 30, height=30)
        self.box_dw_empty = gui.widgetBox(box, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 30, height=30)

        self.create_box(self.box_dw, "debye_waller_factor", "B")

        self.set_dw()

        box = gui.widgetBox(main_box,
                            "Lorentz-Polarization Factor", orientation="vertical",
                            width=self.CONTROL_AREA_WIDTH - 30)

        orangegui.comboBox(box, self, "use_lorentz_polarization_factor", label="Calculate", items=["No", "Yes"], labelWidth=250, orientation="horizontal")

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Therma/Polarization Parameters", height=50, callback=self.send_fit_initialization)

    def set_dw(self):
        self.box_dw.setVisible(self.use_debye_waller_factor==1)
        self.box_dw_empty.setVisible(self.use_debye_waller_factor==0)

    def send_fit_initialization(self):
        try:
            if not self.fit_global_parameters is None:
                send_data = True

                if self.use_debye_waller_factor == 1:
                    congruence.checkStrictlyPositiveNumber(self.debye_waller_factor, "B")

                    if not self.fit_global_parameters.fit_initialization.crystal_structure.use_structure:
                        send_data = ConfirmDialog.confirmed(parent=self, message="Debye Waller factor is better refined when the structural model is activated.\nProceed anyway?")

                if send_data:
                    self.fit_global_parameters.fit_initialization.thermal_polarization_parameters = ThermalPolarizationParameters(debye_waller_factor=None if self.use_debye_waller_factor==0 else self.populate_parameter("debye_waller_factor",
                                                                                                                                                                                                                           ThermalPolarizationParameters.get_parameters_prefix()),
                                                                                                                                  use_lorentz_polarization_factor=self.use_lorentz_polarization_factor==1)

                    self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    def set_data(self, data):
        if not data is None:
            self.fit_global_parameters = data.duplicate()

            if not self.fit_global_parameters.fit_initialization.thermal_polarization_parameters is None:
                self.use_debye_waller_factor = 1 if not self.fit_global_parameters.fit_initialization.thermal_polarization_parameters.debye_waller_factor is None else 0

                if self.use_debye_waller_factor == 1:
                    self.populate_fields("debye_waller_factor",
                                         self.fit_global_parameters.fit_initialization.thermal_polarization_parameters.debye_waller_factor)

                self.use_lorentz_polarization_factor = 1 if self.fit_global_parameters.fit_initialization.thermal_polarization_parameters.use_lorentz_polarization_factor else 0

            self.set_dw()

            if self.is_automatic_run:
                self.send_fit_initialization()



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWThermalPolarization()
    ow.show()
    a.exec_()
    ow.saveSettings()
