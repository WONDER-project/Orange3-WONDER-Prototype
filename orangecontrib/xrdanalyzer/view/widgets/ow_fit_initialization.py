import sys

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QApplication
from PyQt5.QtCore import Qt

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui, ShowTextDialog
from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParameter
from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Reflection, Simmetry
from orangecontrib.xrdanalyzer.controller.fit.init.fft_parameters import FFTInitParameters

class OWFitInitialization(OWGenericWidget):

    name = "Fit Initialization"
    description = "Define Crystal Structure and FFT Parameters"
    icon = "icons/initialization.png"
    priority = 2

    want_main_area = False

    s_max = Setting(9.0)
    n_step = Setting(8192)

    a = Setting(0.0)
    a_fixed = Setting(0)
    a_has_min = Setting(0)
    a_min = Setting(0.0)
    a_has_max = Setting(0)
    a_max = Setting(0.0)
    a_function = Setting(0)
    a_function_value = Setting("")

    #b = Setting(0.0)
    #c = Setting(0.0)

    #alpha = Setting(0.0)
    #beta = Setting(0.0)
    #gamma = Setting(0.0)

    simmetry = Setting(4)

    reflections = Setting("")

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Fit Initialization", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)


        fft_box = gui.widgetBox(main_box,
                                 "FFT", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 30)

        gui.lineEdit(fft_box, self, "s_max", "S_max [nm-1]", labelWidth=250, valueType=float)
        gui.lineEdit(fft_box, self, "n_step", "FFT Steps", labelWidth=250, valueType=float)

        crystal_box = gui.widgetBox(main_box,
                                    "Crystal Structure", orientation="vertical",
                                    width=self.CONTROL_AREA_WIDTH - 30)

        self.cb_simmetry = orangegui.comboBox(crystal_box, self, "simmetry", label="Simmetry", items=Simmetry.tuple(), callback=self.set_simmetry, orientation="horizontal")

        #gui.lineEdit(crystal_box, self, "a", "Cell Parameter [nm]", labelWidth=250, valueType=float)

        self.create_box(crystal_box, "a", "a0 [nm]")

        reflection_box = gui.widgetBox(crystal_box,
                                       "Reflections", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 50)

        orangegui.label(reflection_box, self, "h, k, l, <intensity_name> int <, min value, max value>")

        self.scrollarea = QScrollArea(reflection_box)
        self.scrollarea.setMaximumWidth(self.CONTROL_AREA_WIDTH - 85)
        self.scrollarea.setMinimumWidth(self.CONTROL_AREA_WIDTH - 85)


        self.text_area = gui.textArea(width=self.CONTROL_AREA_WIDTH - 85, readOnly=False)
        self.text_area.setText(self.reflections)

        self.scrollarea.setWidget(self.text_area)
        self.scrollarea.setWidgetResizable(1)

        reflection_box.layout().addWidget(self.scrollarea, alignment=Qt.AlignHCenter)

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Fit Initialization", height=50, callback=self.send_fit_initialization)


    def set_simmetry(self):
        if not CrystalStructure.is_cube(self.cb_simmetry.currentText()):
            QMessageBox.critical(self, "Error",
                                 "Only Cubic Systems are supported",
                                 QMessageBox.Ok)

            self.simmetry = 4

    def send_fit_initialization(self):
        try:
            if not self.fit_global_parameters is None:
                self.reflections = self.text_area.toPlainText()

                congruence.checkStrictlyPositiveNumber(self.s_max, "S Max")
                congruence.checkStrictlyPositiveNumber(self.n_step, "FFT steps")
                congruence.checkEmptyString(self.reflections, "Reflections")

                crystal_structure = CrystalStructure.init_cube(a0=self.populate_parameter("a", CrystalStructure.get_parameters_prefix()),
                                                               simmetry=self.cb_simmetry.currentText())

                crystal_structure.parse_reflections(self.reflections)

                self.fit_global_parameters.fit_initialization.crystal_structure = crystal_structure
                self.fit_global_parameters.fit_initialization.fft_parameters = FFTInitParameters(s_max=self.s_max,
                                                                                                 n_step=self.n_step)

                self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    def set_data(self, data):
        if not data is None:
            self.fit_global_parameters = data.duplicate()

            if not self.fit_global_parameters.fit_initialization.fft_parameters is None:
                self.n_step = self.fit_global_parameters.fit_initialization.fft_parameters.n_step
                self.s_max = self.fit_global_parameters.fit_initialization.fft_parameters.s_max

            if not self.fit_global_parameters.fit_initialization.crystal_structure is None:
                existing_crystal_structure = CrystalStructure.init_cube(a0=FitParameter(value=self.a, fixed=True), simmetry=self.cb_simmetry.currentText())
                existing_crystal_structure.parse_reflections(self.text_area.toPlainText())

                crystal_structure = self.fit_global_parameters.fit_initialization.crystal_structure

                self.a = crystal_structure.a.value

                simmetries = Simmetry.tuple()
                for index in range(0, len(simmetries)):
                    if simmetries[index] == crystal_structure.simmetry:
                        self.simmetry = index

                for reflection in crystal_structure.get_reflections():
                    existing_reflection = existing_crystal_structure.existing_reflection(reflection.h, reflection.k, reflection.l)

                    if existing_reflection is None:
                        existing_crystal_structure.add_reflection(reflection)
                    else:
                        existing_reflection.intensity.value = reflection.intensity.value

                text = ""

                for reflection in existing_crystal_structure.get_reflections():
                    text += reflection.to_text() + "\n"

                self.text_area.setText(text)
                self.reflections = self.text_area.toPlainText()

            if self.is_automatic_run:
                self.send_fit_initialization()



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWFitInitialization()
    ow.show()
    a.exec_()
    ow.saveSettings()
