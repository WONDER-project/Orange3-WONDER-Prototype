import os, sys

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget, QApplication
from PyQt5.QtCore import Qt

from silx.gui.plot.PlotWindow import PlotWindow

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPatternFactory
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui
from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.init.fit_initialization import FitInitialization

class OWDiffractionPattern(OWGenericWidget):

    name = "Load Diffraction Pattern"
    description = "Loads diffraction pattern " \
                  "points from most common file formats"
    icon = "icons/diffraction_pattern.png"
    priority = 1

    want_main_area = True

    filename = Setting("<input file>")
    wavelength = Setting(0.826)

    diffraction_pattern = None

    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=False)

        main_box = gui.widgetBox(self.controlArea,
                                 "Load Diffraction Pattern", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 5, height=600)

        file_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        self.le_filename = gui.lineEdit(file_box,
                                        self,
                                        value="filename",
                                        valueType=str,
                                        label="File",
                                        labelWidth=50)

        orangegui.button(file_box, self, "...", callback=self.open_folders)

        gui.lineEdit(main_box, self, "wavelength", "Wavelength", labelWidth=250, valueType=float)

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Load Data", height=50, callback=self.load_diffraction_pattern)


        self.tabs = gui.tabWidget(self.mainArea)

        self.tab_data = gui.createTabPage(self.tabs, "Data")
        self.tab_plot = gui.createTabPage(self.tabs, "Plot")

        self.plot = PlotWindow()
        self.plot.setDefaultPlotLines(True)
        self.plot.setActiveCurveColor(color="#00008B")
        self.plot.setGraphXLabel(r"2$\theta$")
        self.plot.setGraphYLabel("Intensity")

        self.tab_plot.layout().addWidget(self.plot)

        self.scrollarea = QScrollArea(self.tab_data)
        self.scrollarea.setMinimumWidth(805)
        self.scrollarea.setMinimumHeight(605)

        self.text_area = gui.textArea(height=600, width=800, readOnly=True)

        self.scrollarea.setWidget(self.text_area)
        self.scrollarea.setWidgetResizable(1)

        self.tab_data.layout().addWidget(self.scrollarea, alignment=Qt.AlignHCenter)


    def open_folders(self):
        self.filename=gui.selectFileFromDialog(self,
                                               self.filename,
                                               start_directory=os.curdir)

        self.le_filename.setText(self.filename)

    def load_diffraction_pattern(self):
        try:
            congruence.checkFile(self.filename)

            self.diffraction_pattern = DiffractionPatternFactory.create_diffraction_pattern_from_file(self.filename, self.wavelength)

            self.wavelength = self.diffraction_pattern.wavelength

            self.show_data()

            self.tabs.setCurrentIndex(1)

            self.send("Fit Global Parameters", FitGlobalParameters(fit_initialization=FitInitialization(diffraction_pattern=self.diffraction_pattern)))

        except Exception as e:
            QMessageBox.critical(self, "Error during load",
                                 str(e),
                                 QMessageBox.Ok)

    def show_data(self):
        text = "2Theta [deg], s [Å-1], Intensity"
        x = []
        y = []

        for index in range(0, self.diffraction_pattern.diffraction_points_count()):
            text += "\n" + str(self.diffraction_pattern.get_diffraction_point(index).twotheta) + "  " + \
                    str(self.diffraction_pattern.get_diffraction_point(index).s) + " " + \
                    str(self.diffraction_pattern.get_diffraction_point(index).intensity)

            x.append(self.diffraction_pattern.get_diffraction_point(index).twotheta)
            y.append(self.diffraction_pattern.get_diffraction_point(index).intensity)

        self.plot.addCurve(x, y)
        self.text_area.setText(text)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWDiffractionPattern()
    ow.show()
    a.exec_()
    ow.saveSettings()
