import sys, numpy

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui, ConfirmDialog, ConfirmTextDialog, ShowTextDialog
from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.controller.fit.util.fit_utilities import Utilities, list_of_s_bragg
from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParameter, Boundary
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Reflection
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure_simmetry import Simmetry


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

    simmetry = Setting(2)

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

    limit = Setting(0.0)
    limit_type = Setting(0)

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        crystal_box = gui.widgetBox(self.controlArea,
                                 "Crystal Structure", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)

        self.cb_simmetry = orangegui.comboBox(crystal_box, self, "simmetry", label="Simmetry", items=Simmetry.tuple(), callback=self.set_simmetry, orientation="horizontal")

        self.create_box(crystal_box, "a", "a [nm]")

        orangegui.separator(crystal_box)

        structure_box = gui.widgetBox(crystal_box,
                                       "", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 20)

        orangegui.comboBox(structure_box, self, "use_structure", label="Use Structural Model", items=["No", "Yes"],
                           callback=self.set_structure, labelWidth=350, orientation="horizontal")


        self.structure_box_1 = gui.widgetBox(structure_box,
                                       "", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 30, height=60)

        gui.lineEdit(self.structure_box_1, self, "formula", "Chemical Formula", labelWidth=90, valueType=str)
        self.create_box(self.structure_box_1, "intensity_scale_factor", "I0")

        self.structure_box_2 = gui.widgetBox(structure_box,
                                       "", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 30, height=60)

        orangegui.separator(crystal_box)

        gen_box = gui.widgetBox(crystal_box, "Generate Reflections", orientation="horizontal")

        le_limit = gui.lineEdit(gen_box, self, "limit", "Limit", labelWidth=90, valueType=float, validator=QDoubleValidator())
        cb_limit = orangegui.comboBox(gen_box, self, "limit_type", label="Kind", items=["None", "Nr. Peaks", "2Theta Max"], orientation="horizontal")

        def set_limit(limit_type):
            if limit_type == 0:
                le_limit.setText("-1")
                le_limit.setEnabled(False)
            else:
                le_limit.setEnabled(True)

        cb_limit.currentIndexChanged.connect(set_limit)
        set_limit(self.limit_type)

        gui.button(gen_box, self, "Generate Reflections", callback=self.generate_reflections)



        self.set_structure()

        reflection_box = gui.widgetBox(crystal_box,
                                       "Reflections", orientation="vertical",
                                       width=self.CONTROL_AREA_WIDTH - 50)

        orangegui.label(reflection_box, self, "h, k, l, <intensity_name> int <, min value, max value>")

        self.scrollarea = QScrollArea(reflection_box)
        self.scrollarea.setMaximumWidth(self.CONTROL_AREA_WIDTH - 85)
        self.scrollarea.setMinimumWidth(self.CONTROL_AREA_WIDTH - 85)

        def write_text():
            self.reflections = self.text_area.toPlainText()

        self.text_area = gui.textArea(height=500, width=1000, readOnly=False)
        self.text_area.setText(self.reflections)
        self.text_area.setStyleSheet("font-family: Courier, monospace;")
        self.text_area.textChanged.connect(write_text)

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

            self.simmetry = 2

    def generate_reflections(self):
        if self.populate_parameter("a", "").function:
            QMessageBox.critical(self,
                                 "Error",
                                 "a0 value is a function, generation is not possibile",
                                 QMessageBox.Ok)
            return

        if not self.reflections is None and not self.reflections.strip() == "":
            if not ConfirmDialog.confirmed(self, "Confirm overwriting of exisiting reflections?"):
                return

        if self.limit_type == 0:
            list = list_of_s_bragg(self.a,
                                   simmetry=self.cb_simmetry.currentText())
        elif self.limit_type == 1:
            list = list_of_s_bragg(self.a,
                                   simmetry=self.cb_simmetry.currentText(),
                                   n_peaks=int(self.limit))
        elif self.limit_type == 2:
            if not self.fit_global_parameters is None \
               and not self.fit_global_parameters.fit_initialization is None \
               and not self.fit_global_parameters.fit_initialization.diffraction_pattern is None \
               and not self.fit_global_parameters.fit_initialization.diffraction_pattern.wavelength.function:
                wavelength = self.fit_global_parameters.fit_initialization.diffraction_pattern.wavelength.value

                list = list_of_s_bragg(self.a,
                                       simmetry=self.cb_simmetry.currentText(),
                                       s_max=Utilities.s(numpy.radians(self.limit/2), wavelength))
            else:
                QMessageBox.critical(self,
                                     "Error",
                                     "No wavelenght is available, 2theta limit is not possibile",
                                     QMessageBox.Ok)
                return

        text = ""

        for index in range(0, len(list)):
            h = list[index][0][0]
            k = list[index][0][1]
            l = list[index][0][2]

            text += Reflection(h, k, l, FitParameter(parameter_name="I" + str(h) + str(k) + str(l), value=1000, boundary=Boundary(min_value=0.0))).to_text() + "\n"

        self.text_area.setText(text)

    def send_fit_initialization(self):
        try:
            if not self.fit_global_parameters is None:
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

                if not self.fit_global_parameters.fit_initialization is None \
                   and not self.fit_global_parameters.fit_initialization.diffraction_patterns is None:

                    for index in range(len(self.fit_global_parameters.fit_initialization.diffraction_patterns)):
                        diffraction_pattern = self.fit_global_parameters.fit_initialization.diffraction_patterns[index]

                        if not diffraction_pattern.wavelength.function:
                            wavelength = diffraction_pattern.wavelength.value
                            s_min = diffraction_pattern.get_diffraction_point(0).s
                            s_max = diffraction_pattern.get_diffraction_point(-1).s

                            excluded_reflections = crystal_structure.get_congruence_check(wavelength=wavelength,
                                                                                          min_value=s_min,
                                                                                          max_value=s_max)

                            if not excluded_reflections is None:
                                text_before = "The following reflections lie outside the diffraction pattern nr " + str(index+1) + ":"

                                text = ""
                                for reflection in excluded_reflections:
                                    text += "[" + str(reflection.h) + ", " + str(reflection.k) + ", " + str(reflection.l) +"]\n"

                                text_after = "Proceed anyway?"

                                if not ConfirmTextDialog.confirm_text("Confirm Structure", text,
                                                                      text_after=text_after, text_before=text_before,
                                                                      width=350, parent=self): return

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

            crystal_structure = self.fit_global_parameters.fit_initialization.crystal_structure

            if not crystal_structure is None:
                self.populate_fields("a", crystal_structure.a)
                self.use_structure = 1 if crystal_structure.use_structure else 0

                if self.use_structure == 0:
                    existing_crystal_structure = CrystalStructure.init_cube(a0=self.populate_parameter("a", CrystalStructure.get_parameters_prefix()),
                                                                   simmetry=self.cb_simmetry.currentText())

                elif self.use_structure == 1:
                    self.populate_fields("intensity_scale_factor", crystal_structure.intensity_scale_factor)

                    existing_crystal_structure = CrystalStructure.init_cube(a0=self.populate_parameter("a", CrystalStructure.get_parameters_prefix()),
                                                                   simmetry=self.cb_simmetry.currentText(),
                                                                   use_structure=True,
                                                                   formula=congruence.checkEmptyString(self.formula, "Chemical Formula"),
                                                                   intensity_scale_factor=self.populate_parameter("intensity_scale_factor", CrystalStructure.get_parameters_prefix()))


                if not self.text_area.toPlainText().strip() == "":
                    existing_crystal_structure.parse_reflections(self.text_area.toPlainText())

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
                    text += reflection.to_row() + "\n"

                self.text_area.setText(text)

            if self.is_automatic_run:
                self.send_fit_initialization()



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWCrystalStructure()
    ow.show()
    a.exec_()
    ow.saveSettings()
