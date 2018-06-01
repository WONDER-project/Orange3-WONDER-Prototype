import sys

from PyQt5.QtWidgets import QMessageBox, QApplication

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import ConfirmDialog, gui
from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.init.thermal_polarization_parameters import ThermalPolarizationParameters

class OWLorentzPolarization(OWGenericWidget):

    name = "Lorentz-Polarization Factors"
    description = "Define Lorentz-olarization Factor"
    icon = "icons/lorentz_polarization.png"
    priority = 4

    want_main_area = False

    use_lorentz_polarization_factor = Setting(1)

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Polarization Properties Setting", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=300)

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box, self, "Send Lorentz-Polarization Parameters", height=50, callback=self.send_lorentz_polarization)

        box = gui.widgetBox(main_box,
                            "Lorentz-Polarization Factor", orientation="vertical",
                            width=self.CONTROL_AREA_WIDTH - 30)

        orangegui.comboBox(box, self, "use_lorentz_polarization_factor", label="Calculate", items=["No", "Yes"], labelWidth=250, orientation="horizontal")


    def send_lorentz_polarization(self):
        try:
            if not self.fit_global_parameters is None:

                if self.fit_global_parameters.fit_initialization.thermal_polarization_parameters is None:
                    self.fit_global_parameters.fit_initialization.thermal_polarization_parameters = [ThermalPolarizationParameters(debye_waller_factor=None,
                                                                                                                                  use_lorentz_polarization_factor=self.use_lorentz_polarization_factor==1)]
                else:
                    self.fit_global_parameters.fit_initialization.thermal_polarization_parameters[0].use_lorentz_polarization_factor = self.use_lorentz_polarization_factor==1

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
                self.use_lorentz_polarization_factor = 1 if self.fit_global_parameters.fit_initialization.thermal_polarization_parameters[0].use_lorentz_polarization_factor else 0

            if self.is_automatic_run:
                self.send_lorentz_polarization()



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWLorentzPolarization()
    ow.show()
    a.exec_()
    ow.saveSettings()
