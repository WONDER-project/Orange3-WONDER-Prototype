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
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure,  Simmetry

class OWCrystalStructure(OWGenericWidget):

    name = "Crystal Structure"
    description = "Define Crystal Structure"
    icon = "icons/crystal_structure.png"
    priority = 3

    want_main_area = False

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

    use_structure = Setting(0)
    formula = Setting("")
    intensity_scale_factor = Setting(1.0)
    intensity_scale_factor_fixed = Setting(0)
    intensity_scale_factor_has_min = Setting(0)
    intensity_scale_factor_min = Setting(0.0)
    intensity_scale_factor_has_max = Setting(0)
    intensity_scale_factor_max = Setting(0.0)
    intensity_scale_factor_function = Setting(0)
    intensity_scale_factor_function_value = Setting("")

    reflections = Setting("")

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        crystal_box = gui.widgetBox(self.controlArea,
                                 "Crystal Structure", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)

        self.cb_simmetry = orangegui.comboBox(crystal_box, self, "simmetry", label="Simmetry", items=Simmetry.tuple(), callback=self.set_simmetry, orientation="horizontal")

        self.create_box(crystal_box, "a", "a0 [nm]")

        structure_box = gui.widgetBox(crystal_box,
                                       "", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 20)

        orangegui.comboBox(structure_box, self, "use_structure", label="Use Structural Model", items=["No", "Yes"],
                           callback=self.set_structure, labelWidth=350, orientation="horizontal")


        self.structure_box_1 = gui.widgetBox(structure_box,
                                       "", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 30, height=60)

        gui.lineEdit(self.structure_box_1, self, "formula", "Chemical Formula", labelWidth=150, valueType=str)
        self.create_box(self.structure_box_1, "intensity_scale_factor", "I0")

        self.structure_box_2 = gui.widgetBox(structure_box,
                                       "", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 30, height=60)


        self.set_structure()

        reflection_box = gui.widgetBox(crystal_box,
                                       "Reflections", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 50)

        orangegui.label(reflection_box, self, "h, k, l, <intensity_name> int <, min value, max value>")

        self.scrollarea = QScrollArea(reflection_box)
        self.scrollarea.setMaximumWidth(self.CONTROL_AREA_WIDTH - 85)
        self.scrollarea.setMinimumWidth(self.CONTROL_AREA_WIDTH - 85)

        self.text_area = gui.textArea(height=500, width=1000, readOnly=False)
        self.text_area.setText(self.reflections)
        self.text_area.setStyleSheet("font-family: Courier, monospace;")

        self.scrollarea.setWidget(self.text_area)
        self.scrollarea.setWidgetResizable(1)

        reflection_box.layout().addWidget(self.scrollarea, alignment=Qt.AlignHCenter)

        button_box = gui.widgetBox(crystal_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Send Crystal Structure", height=50, callback=self.send_fit_initialization)


    def set_structure(self):
        self.structure_box_1.setVisible(self.use_structure==1)
        self.structure_box_2.setVisible(self.use_structure==0)

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

                if self.use_structure == 0:
                    crystal_structure = CrystalStructure.init_cube(a0=self.populate_parameter("a", CrystalStructure.get_parameters_prefix()),
                                                                   simmetry=self.cb_simmetry.currentText())

                    crystal_structure.parse_reflections(self.reflections)

                elif self.use_structure == 1:
                    crystal_structure = CrystalStructure.init_cube(a0=self.populate_parameter("a", CrystalStructure.get_parameters_prefix()),
                                                                   simmetry=self.cb_simmetry.currentText(),
                                                                   use_structure=True,
                                                                   formula=congruence.checkEmptyString(self.formula, "Chemical Formula"),
                                                                   intensity_scale_factor=self.populate_parameter("intensity_scale_factor", CrystalStructure.get_parameters_prefix()))

                    crystal_structure.parse_reflections(self.reflections)

                    #intensities will be ignored
                    for reflection in crystal_structure.get_reflections():
                        reflection.intensity.fixed = True

                self.fit_global_parameters.fit_initialization.crystal_structure = crystal_structure

                self.send("Fit Global Parameters", self.fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    def set_data(self, data):
        if not data is None:
            self.fit_global_parameters = data.duplicate()

            if not self.fit_global_parameters.fit_initialization.crystal_structure is None:
                if self.use_structure == 0:
                    existing_crystal_structure = CrystalStructure.init_cube(a0=self.populate_parameter("a", CrystalStructure.get_parameters_prefix()),
                                                                   simmetry=self.cb_simmetry.currentText())

                elif self.use_structure == 1:
                    existing_crystal_structure = CrystalStructure.init_cube(a0=self.populate_parameter("a", CrystalStructure.get_parameters_prefix()),
                                                                   simmetry=self.cb_simmetry.currentText(),
                                                                   use_structure=True,
                                                                   formula=congruence.checkEmptyString(self.formula, "Chemical Formula"),
                                                                   intensity_scale_factor=self.populate_parameter("intensity_scale_factor", CrystalStructure.get_parameters_prefix()))

                existing_crystal_structure.parse_reflections(self.text_area.toPlainText())

                crystal_structure = self.fit_global_parameters.fit_initialization.crystal_structure

                self.populate_fields("a", self.fit_global_parameters.crystal_structure.a)
                self.use_structure = 1 if crystal_structure.use_structure else 0
                self.populate_fields("intensity_scale_factor", self.fit_global_parameters.crystal_structure.intensity_scale_factor)

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
    ow = OWCrystalStructure()
    ow.show()
    a.exec_()
    ow.saveSettings()
