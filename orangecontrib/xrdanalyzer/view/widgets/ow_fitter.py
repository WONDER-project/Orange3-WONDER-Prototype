import os, sys, threading

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont

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
from orangecontrib.xrdanalyzer.controller.fit.fitter_factory import FitterFactory, FitterName
from orangecontrib.xrdanalyzer.controller.fit.fitter_lmfit import LmfitFittingMethods


class OWFitter(OWGenericWidget):
    name = "Fitter"
    description = "Fitter"
    icon = "icons/fit.png"
    priority = 7

    want_main_area = True

    fitter = Setting(1)
    fitting_method = Setting(0)

    n_iterations = Setting(5)
    is_incremental = Setting(1)
    current_iteration = 0

    fit_global_parameters = None

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Fitter", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)


        fitter_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        self.cb_fitter = orangegui.comboBox(fitter_box, self, "fitter", label="Fitter", items=FitterName.tuple(), callback=self.set_fitter, orientation="horizontal")

        self.fitter_box_1 = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25,
                                   height=30)

        self.fitter_box_2 = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25,
                                   height=30)


        self.cb_fitting_method = orangegui.comboBox(self.fitter_box_2, self, "fitting_method", label="Method", items=LmfitFittingMethods.tuple(), orientation="horizontal")


        self.set_fitter()

        iteration_box = gui.widgetBox(main_box,
                                 "", orientation="horizontal",
                                 width=250)

        gui.lineEdit(iteration_box, self, "n_iterations", "Nr. Iterations", labelWidth=80, valueType=int)
        orangegui.checkBox(iteration_box, self, "is_incremental", "Incremental")

        iteration_box = gui.widgetBox(main_box,
                                 "", orientation="vertical",
                                 width=250)

        self.le_current_iteration = gui.lineEdit(iteration_box, self, "current_iteration", "Current Iteration", labelWidth=120, valueType=int, orientation="horizontal")
        self.le_current_iteration.setReadOnly(True)
        font = QFont(self.le_current_iteration.font())
        font.setBold(True)
        self.le_current_iteration.setFont(font)
        palette = QPalette(self.le_current_iteration.palette())
        palette.setColor(QPalette.Text, QColor('dark blue'))
        palette.setColor(QPalette.Base, QColor(243, 240, 160))
        self.le_current_iteration.setPalette(palette)

        button_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)


        gui.button(button_box,  self, "Fit", height=50, callback=self.do_fit)

        self.tabs = gui.tabWidget(self.mainArea)

        self.tab_fit_in = gui.createTabPage(self.tabs, "Fit Input Parameters")
        self.tab_plot = gui.createTabPage(self.tabs, "Plot")
        self.tab_data = gui.createTabPage(self.tabs, "Fit Output Raw Data")
        self.tab_fit_out = gui.createTabPage(self.tabs, "Fit Output Parameters")

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

        # -------------------

        self.scrollarea_fit_in = QScrollArea(self.tab_fit_in)
        self.scrollarea_fit_in.setMinimumWidth(805)
        self.scrollarea_fit_in.setMinimumHeight(605)

        self.text_area_fit_in = gui.textArea(height=600, width=800, readOnly=True)

        self.scrollarea_fit_in.setWidget(self.text_area_fit_in)
        self.scrollarea_fit_in.setWidgetResizable(1)

        self.tab_fit_in.layout().addWidget(self.scrollarea_fit_in, alignment=Qt.AlignHCenter)

        # -------------------

        self.scrollarea_fit_out = QScrollArea(self.tab_fit_out)
        self.scrollarea_fit_out.setMinimumWidth(805)
        self.scrollarea_fit_out.setMinimumHeight(605)

        self.text_area_fit_out = gui.textArea(height=600, width=800, readOnly=True)

        self.scrollarea_fit_out.setWidget(self.text_area_fit_out)
        self.scrollarea_fit_out.setWidgetResizable(1)

        self.tab_fit_out.layout().addWidget(self.scrollarea_fit_out, alignment=Qt.AlignHCenter)

    def set_fitter(self):
        self.fitter_box_1.setVisible(self.fitter == 0)
        self.fitter_box_2.setVisible(self.fitter == 1)

    def do_fit(self):
        try:
            if not self.fit_global_parameters is None:
                congruence.checkStrictlyPositiveNumber(self.n_iterations, "Nr. Iterations")

                self.progressBarInit()

                fitted_fit_global_parameters = self.fit_global_parameters

                for iteration in range(1, self.n_iterations + 1):

                    self.progressBarSet(int(iteration/self.n_iterations)*100)
                    self.setStatusMessage("Fitting iteration nr. " + str(iteration))

                    fitter = FitterFactory.create_fitter(fitter_name=self.cb_fitter.currentText(),
                                                         fitting_method=self.cb_fitting_method.currentText())

                    self.fitted_pattern, fitted_fit_global_parameters = fitter.do_fit(fit_global_parameters=fitted_fit_global_parameters)

                    self.show_data()

                    self.text_area_fit_out.setText(fitted_fit_global_parameters.to_text())

                    self.tabs.setCurrentIndex(1)

                self.setStatusMessage("Fitting procedure completed")

                if self.is_incremental == 1:
                    self.fit_global_parameters = fitted_fit_global_parameters.duplicate()
                    self.text_area_fit_in.setText(self.fit_global_parameters.to_text())

                self.send("Fit Global Parameters", fitted_fit_global_parameters)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            raise e

        self.setStatusMessage("")
        self.progressBarFinished()


    def set_data(self, data):
        if not data is None:
            self.fit_global_parameters = data.duplicate()

            self.text_area_fit_in.setText(self.fit_global_parameters.to_text())
            self.tabs.setCurrentIndex(0)

            if self.is_automatic_run:
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

        self.plot.addCurve(x, y, legend="data", symbol='o', color="blue")
        self.plot.addCurve(x, yf, legend="fit", color="red")

        self.text_area.setText(text)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWDiffractionPattern()
    ow.show()
    a.exec_()
    ow.saveSettings()
