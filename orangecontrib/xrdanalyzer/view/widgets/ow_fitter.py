import os, sys

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget, QApplication
from PyQt5.QtCore import Qt

from silx.gui.plot.PlotWindow import PlotWindow

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui, ShowTextDialog
from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPatternFactory

from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParameter
from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.init.fit_initialization import FitInitialization
from orangecontrib.xrdanalyzer.controller.fit.init.crystal_structure import CrystalStructure, Reflection, Simmetry
from orangecontrib.xrdanalyzer.controller.fit.init.fft_parameters import FFTInitParameters
from orangecontrib.xrdanalyzer.controller.fit.fitter import FitterFactory



class OWFitter(OWGenericWidget):

    name = "Fitter"
    description = "Fitter"
    icon = "icons/fit.png"
    priority = 7

    want_main_area = True

    fit_global_parameters = None

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Fitter", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)


        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        gui.button(button_box,  self, "Fit", height=50, callback=self.do_fit)

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


    def do_fit(self):
        try:
            if not self.fit_global_parameters is None:
                fitter = FitterFactory.create_fitter()

                self.fitted_pattern = fitter.do_fit(self.fit_global_parameters)

                self.show_data()

                fitted_fit_global_parameters = self.fit_global_parameters # TODO: Da sostituire con i calcolati dal fit

                self.send("Fit Global Parameters", fitted_fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            raise e

    def set_data(self, data):
        self.fit_global_parameters = data

        if not self.fit_global_parameters is None and self.is_automatic_run:
            self.do_fit()

    def show_data(self):
        diffraction_pattern = self.fit_global_parameters.fit_initialization.diffraction_pattern

        text = "2Theta [deg], s [Å-1], Intensity"
        x = []
        y = []
        yf = []

        for index in range(0, self.fitted_pattern.diffraction_points_count()):
            text += "\n" + str(self.fitted_pattern.get_diffraction_point(index).twotheta) + "  " + \
                    str(self.fitted_pattern.get_diffraction_point(index).s) + " " + \
                    str(self.fitted_pattern.get_diffraction_point(index).intensity)

            x.append(diffraction_pattern.get_diffraction_point(index).twotheta)
            y.append(diffraction_pattern.get_diffraction_point(index).intensity)
            yf.append(self.fitted_pattern.get_diffraction_point(index).intensity)

        self.plot.addCurve(x, y, color="blue", symbol='o')
        self.plot.addCurve(x, yf, color="red")

        self.text_area.setText(text)





if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWDiffractionPattern()
    ow.show()
    a.exec_()
    ow.saveSettings()
