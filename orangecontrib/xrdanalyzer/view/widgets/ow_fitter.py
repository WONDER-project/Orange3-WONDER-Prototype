import sys, numpy

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont, QTextCursor

from silx.gui.plot.PlotWindow import PlotWindow

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui, EmittingStream
from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters
from orangecontrib.xrdanalyzer.controller.fit.fitter_factory import FitterFactory, FitterName


class OWFitter(OWGenericWidget):
    name = "Fitter"
    description = "Fitter"
    icon = "icons/fit.png"
    priority = 8

    want_main_area = True

    fitter_name = Setting(0)
    fitting_method = Setting(0)

    n_iterations = Setting(5)
    is_incremental = Setting(1)
    current_iteration = 0
    fitted_fit_global_parameters = None

    free_output_parameters = Setting("")

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    standard_output = sys.stdout

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Fitter", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 10, height=600)


        fitter_box = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25)

        self.cb_fitter = orangegui.comboBox(fitter_box, self, "fitter_name", label="Fitter", items=FitterName.tuple(), callback=self.set_fitter, orientation="horizontal")

        self.fitter_box_1 = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25,
                                   height=30)

        self.fitter_box_2 = gui.widgetBox(main_box,
                                   "", orientation="horizontal",
                                   width=self.CONTROL_AREA_WIDTH-25,
                                   height=30)


        self.cb_fitting_method = orangegui.comboBox(self.fitter_box_2, self, "fitting_method", label="Method", items=[], orientation="horizontal")

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


        fit_button = gui.button(button_box,  self, "Fit", height=50, width=300, callback=self.do_fit)

        font = QFont(fit_button.font())
        font.setBold(True)
        font.setPixelSize(20)
        fit_button.setFont(font)
        palette = QPalette(fit_button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('dark blue'))
        fit_button.setPalette(palette) # assign new palette

        gui.button(button_box,  self, "Send Current Fit", height=50, callback=self.send_current_fit)

        tabs = gui.tabWidget(main_box)
        tab_free_out = gui.createTabPage(tabs, "Free Output Parameters")

        self.scrollarea_free_out = QScrollArea(tab_free_out)
        self.scrollarea_free_out.setMinimumWidth(self.CONTROL_AREA_WIDTH-45)
        self.scrollarea_free_out.setMinimumHeight(260)

        self.text_area_free_out = gui.textArea(height=1000, width=1000, readOnly=False)
        self.text_area_free_out.setText(self.free_output_parameters)

        self.scrollarea_free_out.setWidget(self.text_area_free_out)
        self.scrollarea_free_out.setWidgetResizable(1)

        tab_free_out.layout().addWidget(self.scrollarea_free_out, alignment=Qt.AlignHCenter)

        self.tabs = gui.tabWidget(self.mainArea)

        self.tab_fit_in = gui.createTabPage(self.tabs, "Fit Input Parameters")
        self.tab_plot = gui.createTabPage(self.tabs, "Plot")
        self.tab_data = gui.createTabPage(self.tabs, "Fit Output Raw Data")
        self.tab_fit_out = gui.createTabPage(self.tabs, "Fit Output Parameters")

        self.tabs_plot = gui.tabWidget(self.tab_plot)

        self.tab_plot_fit = gui.createTabPage(self.tabs_plot, "Fit")
        self.tab_plot_size = gui.createTabPage(self.tabs_plot, "Size Distribution")
        self.tab_plot_strain = gui.createTabPage(self.tabs_plot, "Warren's Plot")

        self.std_output = gui.textArea(height=100, width=800)

        out_box = gui.widgetBox(self.mainArea, "System Output", addSpace=False, orientation="horizontal")
        out_box.layout().addWidget(self.std_output)

        self.plot_fit = PlotWindow()
        self.plot_fit.setDefaultPlotLines(True)
        self.plot_fit.setActiveCurveColor(color="#00008B")
        self.plot_fit.setGraphXLabel(r"2$\theta$")
        self.plot_fit.setGraphYLabel("Intensity")

        self.tab_plot_fit.layout().addWidget(self.plot_fit)

        self.plot_size = PlotWindow()
        self.plot_size.setDefaultPlotLines(True)
        self.plot_size.setActiveCurveColor(color="#00008B")
        self.plot_size.setGraphTitle("Crystalline Domains Size Distribution")
        self.plot_size.setGraphXLabel(r"D [nm]")
        self.plot_size.setGraphYLabel("Frequency")

        self.tab_plot_size.layout().addWidget(self.plot_size)

        self.plot_strain = PlotWindow(control=True)
        self.plot_strain.getLegendsDockWidget().show()
        self.plot_strain.setDefaultPlotLines(True)
        self.plot_strain.setActiveCurveColor(color="#00008B")
        self.plot_strain.setGraphTitle("Warren's plot")
        self.plot_strain.setGraphXLabel(r"L [nm]")
        self.plot_strain.setGraphYLabel("$\sqrt{{\Delta}L^{2}}$ [nm]")

        self.tab_plot_strain.layout().addWidget(self.plot_strain)

        self.scrollarea = QScrollArea(self.tab_data)
        self.scrollarea.setMinimumWidth(805)
        self.scrollarea.setMinimumHeight(505)

        self.text_area = gui.textArea(height=500, width=800, readOnly=True)

        self.scrollarea.setWidget(self.text_area)
        self.scrollarea.setWidgetResizable(1)

        self.tab_data.layout().addWidget(self.scrollarea, alignment=Qt.AlignHCenter)

        # -------------------

        self.scrollarea_fit_in = QScrollArea(self.tab_fit_in)
        self.scrollarea_fit_in.setMinimumWidth(805)
        self.scrollarea_fit_in.setMinimumHeight(505)

        self.text_area_fit_in = gui.textArea(height=500, width=800, readOnly=True)

        self.scrollarea_fit_in.setWidget(self.text_area_fit_in)
        self.scrollarea_fit_in.setWidgetResizable(1)

        self.tab_fit_in.layout().addWidget(self.scrollarea_fit_in, alignment=Qt.AlignHCenter)

        # -------------------

        self.scrollarea_fit_out = QScrollArea(self.tab_fit_out)
        self.scrollarea_fit_out.setMinimumWidth(805)
        self.scrollarea_fit_out.setMinimumHeight(505)

        self.text_area_fit_out = gui.textArea(height=500, width=800, readOnly=True)

        self.scrollarea_fit_out.setWidget(self.text_area_fit_out)
        self.scrollarea_fit_out.setWidgetResizable(1)

        self.tab_fit_out.layout().addWidget(self.scrollarea_fit_out, alignment=Qt.AlignHCenter)

    def write_stdout(self, text):
        cursor = self.std_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.std_output.setTextCursor(cursor)
        self.std_output.ensureCursorVisible()

    def set_fitter(self):
        self.fitter_box_1.setVisible(self.fitter_name <= 1)
        self.fitter_box_2.setVisible(self.fitter_name == 2)

    def do_fit(self):
        try:
            if not self.fit_global_parameters is None:
                self.free_output_parameters = self.text_area_free_out.toPlainText()

                congruence.checkStrictlyPositiveNumber(self.n_iterations, "Nr. Iterations")

                self.fit_global_parameters.set_n_max_iterations(self.n_iterations)
                self.fit_global_parameters.set_convergence_reached(False)
                self.fit_global_parameters.free_output_parameters.parse_formulas(self.free_output_parameters)

                initial_fit_global_parameters = self.fit_global_parameters.duplicate()

                if self.is_incremental == 1:
                    if self.current_iteration == 0:
                        self.fitter = FitterFactory.create_fitter(fitter_name=self.cb_fitter.currentText(),
                                                                  fitting_method=self.cb_fitting_method.currentText())

                        self.fitter.init_fitter(initial_fit_global_parameters)
                else:
                    self.fitter = FitterFactory.create_fitter(fitter_name=self.cb_fitter.currentText(),
                                                              fitting_method=self.cb_fitting_method.currentText())

                    self.fitter.init_fitter(initial_fit_global_parameters)
                    self.current_iteration = 0

                self.fitted_fit_global_parameters = initial_fit_global_parameters
                self.current_running_iteration = 0

                sys.stdout = EmittingStream(textWritten=self.write_stdout)

                fit_thread = FitThread(self)
                fit_thread.begin.connect(self.fit_begin)
                fit_thread.update.connect(self.fit_update)
                fit_thread.finished.connect(self.fit_completed)
                fit_thread.start()

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            sys.stdout = self.standard_ouput

            if self.IS_DEVELOP: raise e

        self.setStatusMessage("")
        self.progressBarFinished()

    def send_current_fit(self):
        if not self.fit_global_parameters is None:
            self.send("Fit Global Parameters", self.fit_global_parameters.duplicate())

    def set_data(self, data):
        if not data is None:
            self.fit_global_parameters = data.duplicate()

            self.fit_global_parameters.free_output_parameters.parse_formulas(self.text_area_free_out.toPlainText()) # existing parameters

            self.text_area_free_out.setText(self.fit_global_parameters.free_output_parameters.to_python_code())
            self.free_output_parameters = self.text_area_free_out.toPlainText()

            self.text_area_fit_in.setText(self.fit_global_parameters.to_text())
            self.tabs.setCurrentIndex(0)

            if self.is_automatic_run:
                self.do_fit()

    def show_data(self):
        diffraction_pattern = self.fit_global_parameters.fit_initialization.diffraction_pattern

        text = "2Theta [deg], s [Å-1], Intensity, Residual"
        x = []
        y = []
        yf = []
        res = []

        for index in range(0, self.fitted_pattern.diffraction_points_count()):
            text += "\n" + str(self.fitted_pattern.get_diffraction_point(index).twotheta) + "  " + \
                    str(self.fitted_pattern.get_diffraction_point(index).s) + " " + \
                    str(self.fitted_pattern.get_diffraction_point(index).intensity) + " " + \
                    str(self.fitted_pattern.get_diffraction_point(index).error) + " "

            x.append(diffraction_pattern.get_diffraction_point(index).twotheta)
            y.append(diffraction_pattern.get_diffraction_point(index).intensity)
            yf.append(self.fitted_pattern.get_diffraction_point(index).intensity)
            res.append(self.fitted_pattern.get_diffraction_point(index).error)

        self.text_area.setText(text)

        max_res = numpy.max(res)

        res = -10 + (res-max_res)

        self.plot_fit.addCurve(x, y, legend="data", symbol='o', color="blue")
        self.plot_fit.addCurve(x, yf, legend="fit", color="red")
        self.plot_fit.addCurve(x, res, legend="residual", color="green")

        title =  "WSS, SS: " + str(self.fit_data.wss) + ", " + str(self.fit_data.ss) + "\n"
        title += "GOF: " + str(self.fit_data.gof())

        self.plot_fit.setGraphTitle(title)

        if not self.fit_global_parameters.size_parameters is None:
            x, y = self.fit_global_parameters.size_parameters.get_distribution()

            self.plot_size.addCurve(x, y, legend="distribution", color="blue")

        if not self.fit_global_parameters.strain_parameters is None:
            crystal_structure = self.fit_global_parameters.fit_initialization.crystal_structure

            colors = ['blue', 'red', 'green']

            for index in range (0, 3):
                h = crystal_structure.get_reflection(index).h
                k = crystal_structure.get_reflection(index).k
                l = crystal_structure.get_reflection(index).l

                x, y = self.fit_global_parameters.strain_parameters.get_warren_plot(h, k, l)

                self.plot_strain.addCurve(x, y, legend=str(h) + str(k) + str(l), color=colors[index])





##########################################
# THREADING
##########################################
    def fit_begin(self):
        from PyQt5.QtCore import QMutex

        mutex = QMutex()
        mutex.lock()

        self.progressBarInit()
        self.setStatusMessage("Fitting procedure started")

        mutex.unlock()

    def fit_update(self):
        from PyQt5.QtCore import QMutex

        mutex = QMutex()
        mutex.lock()

        try:
            self.current_iteration += 1
            self.current_running_iteration += 1

            self.progressBarSet(int(self.current_running_iteration*100/self.n_iterations))
            self.setStatusMessage("Fit iteration nr. " + str(self.current_iteration) + "/" + str(self.n_iterations) + " completed")

            self.show_data()

            self.text_area_fit_out.setText(self.fitted_fit_global_parameters.to_text())

            if self.current_iteration == 1:
                self.tabs.setCurrentIndex(1)
                self.tabs_plot.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

        mutex.unlock()


    def fit_completed(self):
        sys.stdout = self.standard_output

        self.setStatusMessage("Fitting procedure completed")

        if self.is_incremental == 1:
            self.fit_global_parameters = self.fitted_fit_global_parameters.duplicate()
            self.text_area_fit_in.setText(self.fit_global_parameters.to_text())

        self.send("Fit Global Parameters", self.fitted_fit_global_parameters)

        self.progressBarFinished()

from PyQt5.QtCore import QThread, pyqtSignal

class FitThread(QThread):

    begin = pyqtSignal()
    update = pyqtSignal()

    def __init__(self, fitter_widget):
        super(FitThread, self).__init__(fitter_widget)
        self.fitter_widget = fitter_widget

    def run(self):
        try:
            self.begin.emit()

            for iteration in range(1, self.fitter_widget.n_iterations + 1):
                self.fitter_widget.fitted_pattern, \
                self.fitter_widget.fitted_fit_global_parameters, \
                self.fitter_widget.fit_data = \
                    self.fitter_widget.fitter.do_fit(current_fit_global_parameters=self.fitter_widget.fitted_fit_global_parameters,
                                                     current_iteration=iteration)

                if self.fitter_widget.fitted_fit_global_parameters.is_convergence_reached(): break

                self.update.emit()
        except Exception as e:
            QMessageBox.critical(self.fitter_widget, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.fitter_widget.IS_DEVELOP: raise e

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWFitter()
    ow.show()
    a.exec_()
    ow.saveSettings()
