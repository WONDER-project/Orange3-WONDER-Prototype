import sys

from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QDoubleValidator

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import ConfirmDialog, gui

from orangecontrib.xrdanalyzer import is_recovery

if not is_recovery:
    from orangecontrib.xrdanalyzer.util import congruence
    from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
    from orangecontrib.xrdanalyzer.controller.fit.init.thermal_polarization_parameters import ThermalPolarizationParameters
else:
    from orangecontrib.xrdanalyzer.recovery.util import congruence
    from orangecontrib.xrdanalyzer.recovery.controller.fit.fit_global_parameters import FitGlobalParameters
    from orangecontrib.xrdanalyzer.recovery.controller.fit.init.thermal_polarization_parameters import ThermalPolarizationParameters

class OWLorentzPolarization(OWGenericWidget):

    name = "Lorentz-Polarization Factors"
    description = "Define Lorentz-Polarization Factor"
    icon = "icons/lorentz_polarization.png"
    priority = 4

    want_main_area = False

    use_lorentz_factor = Setting(1)
    use_polarization_factor = Setting(0)
    use_twotheta_mono = Setting(1)
    twotheta_mono = Setting(28.443)

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Lorentz-Polarization Factors Setting", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=300)

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box, self, "Send Lorentz-Polarization Parameters", height=50, callback=self.send_lorentz_polarization)

        box = gui.widgetBox(main_box,
                            "Lorentz-Polarization Factors", orientation="vertical",
                            width=self.CONTROL_AREA_WIDTH - 30)

        orangegui.comboBox(box, self, "use_lorentz_factor", label="Add Lorentz Factor", items=["No", "Yes"], labelWidth=250, orientation="horizontal")

        orangegui.separator(box)

        orangegui.comboBox(box, self, "use_polarization_factor", label="Add Polarization Factor", items=["No", "Yes"], labelWidth=250,
                           orientation="horizontal", callback=self.set_Polarization)

        self.polarization_box = gui.widgetBox(box, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 30, height=70)
        self.polarization_box_empty = gui.widgetBox(box, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 30, height=70)

        orangegui.comboBox(self.polarization_box, self, "use_twotheta_mono", label="Use Monochromator", items=["No", "Yes"], labelWidth=250,
                           orientation="horizontal", callback=self.set_Monochromator)

        self.monochromator_box = gui.widgetBox(self.polarization_box, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 50, height=35)
        self.monochromator_box_empty = gui.widgetBox(self.polarization_box, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH - 50, height=35)

        gui.lineEdit(self.monochromator_box, self, "twotheta_mono", "2\u03B8 Monochromator [deg]", labelWidth=260, valueType=float, validator=QDoubleValidator())

        self.set_Polarization()

    def set_Monochromator(self):
        self.monochromator_box.setVisible(self.use_twotheta_mono==1)
        self.monochromator_box_empty.setVisible(self.use_twotheta_mono==0)

    def set_Polarization(self):
        self.polarization_box.setVisible(self.use_polarization_factor==1)
        self.polarization_box_empty.setVisible(self.use_polarization_factor==0)
        if self.use_polarization_factor==1: self.set_Monochromator()

    def send_lorentz_polarization(self):
        try:
            if not self.fit_global_parameters is None:
                if self.use_polarization_factor == 1 and self.use_twotheta_mono==1:
                    congruence.checkStrictlyPositiveAngle(self.twotheta_mono, "2\u03B8 Monochromator")

                if self.fit_global_parameters.fit_initialization.thermal_polarization_parameters is None:
                    self.fit_global_parameters.fit_initialization.thermal_polarization_parameters = \
                        [ThermalPolarizationParameters(debye_waller_factor=None,
                                                       use_lorentz_factor=self.use_lorentz_factor==1,
                                                       use_polarization_factor=self.use_polarization_factor,
                                                       twotheta_mono=None if (self.use_polarization_factor==0 or self.use_twotheta_mono==0) else self.twotheta_mono)]
                else:
                    self.fit_global_parameters.fit_initialization.thermal_polarization_parameters[0].use_lorentz_factor = self.use_lorentz_factor==1
                    self.fit_global_parameters.fit_initialization.thermal_polarization_parameters[0].use_polarization_factor = self.use_polarization_factor==1
                    self.fit_global_parameters.fit_initialization.thermal_polarization_parameters[0].twotheta_mono = None if (self.use_polarization_factor==0 or self.use_twotheta_mono==0) else self.twotheta_mono

                self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    def set_data(self, data):
        if not data is None:
            self.fit_global_parameters = data.duplicate()

            if not self.fit_global_parameters.fit_initialization.crystal_structures is None:
                crystal_structure = self.fit_global_parameters.fit_initialization.crystal_structures[0]

                if not crystal_structure.use_structure:
                    QMessageBox.warning(self, "Warning", "Lorentz-Polarization Factor should be used when a structural model is selected in the crystal structure")

            if not self.fit_global_parameters.fit_initialization.thermal_polarization_parameters is None:
                self.use_lorentz_factor = 1 if self.fit_global_parameters.fit_initialization.thermal_polarization_parameters[0].use_lorentz_factor else self.use_lorentz_factor
                self.use_polarization_factor = 1 if self.fit_global_parameters.fit_initialization.thermal_polarization_parameters[0].use_polarization_factor else self.use_polarization_factor
                if self.use_polarization_factor:
                    tth = self.fit_global_parameters.fit_initialization.thermal_polarization_parameters[0].twotheta_mono
                    self.twotheta_mono = self.twotheta_mono if tth is None else tth

            if self.is_automatic_run:
                self.send_lorentz_polarization()



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWLorentzPolarization()
    ow.show()
    a.exec_()
    ow.saveSettings()
