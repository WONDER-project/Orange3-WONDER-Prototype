import sys, numpy, os

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QApplication, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QFileDialog
from PyQt5.QtCore import Qt, QMutex
from PyQt5.QtGui import QColor, QFont, QTextCursor, QIntValidator

from silx.gui.plot.PlotWindow import PlotWindow
from silx.gui.plot.LegendSelector import LegendsDockWidget
from silx.gui import qt

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui, ConfirmDialog, EmittingStream
from orangecontrib.xrdanalyzer.util import congruence

from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import PARAM_HWMAX, PARAM_HWMIN
from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters, FreeOutputParameters
from orangecontrib.xrdanalyzer.controller.fit.fitter_factory import FitterFactory, FitterName


class OWFitter(OWGenericWidget):
    name = "Fitter"
    description = "Fitter"
    icon = "icons/fit.png"
    priority = 60

    want_main_area = True
    standard_output = sys.stdout

    fitter_name = Setting(0)
    fitting_method = Setting(0)

    n_iterations = Setting(5)
    is_incremental = Setting(1)
    current_iteration = 0
    free_output_parameters_text = Setting("")
    save_file_name = Setting("fit_output.dat")

    horizontal_headers = ["Name", "Value", "Min", "Max", "Fixed", "Function", "Expression", "Var"]

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]


    fitted_fit_global_parameters = None
    current_wss = []
    current_gof = []

    stop_fit = False

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

        iteration_box = gui.widgetBox(main_box, "", orientation="horizontal", width=250)

        gui.lineEdit(iteration_box, self, "n_iterations", "Nr. Iterations", labelWidth=80, valueType=int, validator=QIntValidator())
        orangegui.checkBox(iteration_box, self, "is_incremental", "Incremental")

        iteration_box = gui.widgetBox(main_box, "", orientation="vertical", width=250)

        self.le_current_iteration = gui.lineEdit(iteration_box, self, "current_iteration", "Current Iteration", labelWidth=120, valueType=int, orientation="horizontal")
        self.le_current_iteration.setReadOnly(True)
        self.le_current_iteration.setStyleSheet("background-color: #FAFAB0; color: #252468")
        font = QFont(self.le_current_iteration.font())
        font.setBold(True)
        self.le_current_iteration.setFont(font)

        button_box = gui.widgetBox(main_box, "", orientation="vertical", width=self.CONTROL_AREA_WIDTH-25, height=90)

        button_box_1 = gui.widgetBox(button_box, "", orientation="horizontal")

        self.fit_button = gui.button(button_box_1,  self, "Fit", height=50, callback=self.do_fit)
        self.fit_button.setStyleSheet("color: #252468")
        font = QFont(self.fit_button.font())
        font.setBold(True)
        font.setPixelSize(18)
        self.fit_button.setFont(font)

        self.stop_fit_button = gui.button(button_box_1,  self, "STOP", height=50, callback=self.stop_fit)
        self.stop_fit_button.setStyleSheet("color: red")
        font = QFont(self.stop_fit_button.font())
        font.setBold(True)
        font.setItalic(True)
        self.stop_fit_button.setFont(font)

        button_box_2 = gui.widgetBox(button_box, "", orientation="horizontal")

        gui.button(button_box_2,  self, "Send Current Fit", height=50, callback=self.send_current_fit)
        gui.button(button_box_2,  self, "Save Data", height=50, callback=self.save_data)

        orangegui.separator(main_box, 5)

        tabs = gui.tabWidget(main_box)
        tab_free_out = gui.createTabPage(tabs, "Free Output Parameters")

        self.scrollarea_free_out = QScrollArea(tab_free_out)
        self.scrollarea_free_out.setMinimumWidth(self.CONTROL_AREA_WIDTH-45)
        self.scrollarea_free_out.setMinimumHeight(260)

        def write_text():
            self.free_output_parameters_text = self.text_area_free_out.toPlainText()

        self.text_area_free_out = gui.textArea(height=1000, width=1000, readOnly=False)
        self.text_area_free_out.setText(self.free_output_parameters_text)
        self.text_area_free_out.textChanged.connect(write_text)

        self.scrollarea_free_out.setWidget(self.text_area_free_out)
        self.scrollarea_free_out.setWidgetResizable(1)

        tab_free_out.layout().addWidget(self.scrollarea_free_out, alignment=Qt.AlignHCenter)

        self.tabs = gui.tabWidget(self.mainArea)

        self.tab_fit_in  = gui.createTabPage(self.tabs, "Fit Input Parameters")
        self.tab_plot    = gui.createTabPage(self.tabs, "Plots")
        self.tab_fit_out = gui.createTabPage(self.tabs, "Fit Output Parameters")

        self.tabs_plot = gui.tabWidget(self.tab_plot)

        self.tab_plot_fit    = gui.createTabPage(self.tabs_plot, "Fit")
        self.tab_plot_size   = gui.createTabPage(self.tabs_plot, "Size Distribution")
        self.tab_plot_strain = gui.createTabPage(self.tabs_plot, "Warren's Plot")

        self.std_output = gui.textArea(height=100, width=800)

        out_box = gui.widgetBox(self.mainArea, "System Output", addSpace=False, orientation="horizontal")
        out_box.layout().addWidget(self.std_output)

        self.tabs_plot_fit = gui.tabWidget(self.tab_plot_fit)

        self.tab_plot_fit_data = gui.createTabPage(self.tabs_plot_fit, "Data")
        self.tab_plot_fit_wss  = gui.createTabPage(self.tabs_plot_fit, "W.S.S.")
        self.tab_plot_fit_gof  = gui.createTabPage(self.tabs_plot_fit, "G.o.F.")

        self.plot_fit = PlotWindow()
        self.plot_fit.setDefaultPlotLines(True)
        self.plot_fit.setActiveCurveColor(color="#00008B")
        self.plot_fit.setGraphXLabel(r"2$\theta$")
        self.plot_fit.setGraphYLabel("Intensity")

        self.tab_plot_fit_data.layout().addWidget(self.plot_fit)

        self.plot_fit_wss = PlotWindow()
        self.plot_fit_wss.setDefaultPlotLines(True)
        self.plot_fit_wss.setActiveCurveColor(color="#00008B")
        self.plot_fit_wss.setGraphXLabel("Iteration")
        self.plot_fit_wss.setGraphYLabel("WSS")

        self.tab_plot_fit_wss.layout().addWidget(self.plot_fit_wss)

        self.plot_fit_gof = PlotWindow()
        self.plot_fit_gof.setDefaultPlotLines(True)
        self.plot_fit_gof.setActiveCurveColor(color="#00008B")
        self.plot_fit_gof.setGraphXLabel("Iteration")
        self.plot_fit_gof.setGraphYLabel("GOF")

        self.tab_plot_fit_gof.layout().addWidget(self.plot_fit_gof)

        self.plot_size = PlotWindow()
        self.plot_size.setDefaultPlotLines(True)
        self.plot_size.setActiveCurveColor(color="#00008B")
        self.plot_size.setGraphTitle("Crystalline Domains Size Distribution")
        self.plot_size.setGraphXLabel(r"D [nm]")
        self.plot_size.setGraphYLabel("Frequency")

        self.tab_plot_size.layout().addWidget(self.plot_size)

        self.plot_strain = PlotWindow(control=True)
        legendsDockWidget = LegendsDockWidget(plot=self.plot_strain)
        self.plot_strain._legendsDockWidget = legendsDockWidget
        self.plot_strain._dockWidgets.append(legendsDockWidget)
        self.plot_strain.addDockWidget(qt.Qt.RightDockWidgetArea, legendsDockWidget)
        self.plot_strain._legendsDockWidget.setFixedWidth(120)
        self.plot_strain.getLegendsDockWidget().show()

        self.plot_strain.setDefaultPlotLines(True)
        self.plot_strain.setActiveCurveColor(color="#00008B")
        self.plot_strain.setGraphTitle("Warren's plot")
        self.plot_strain.setGraphXLabel(r"L [nm]")
        self.plot_strain.setGraphYLabel("$\sqrt{<{\Delta}L^{2}>}$ [nm]")

        self.tab_plot_strain.layout().addWidget(self.plot_strain)

        # -------------------

        self.scrollarea_fit_in = QScrollArea(self.tab_fit_in)
        self.scrollarea_fit_in.setMinimumWidth(805)
        self.scrollarea_fit_in.setMinimumHeight(505)

        self.table_fit_in = self.create_table_widget()

        self.scrollarea_fit_in.setWidget(self.table_fit_in)
        self.scrollarea_fit_in.setWidgetResizable(1)

        self.tab_fit_in.layout().addWidget(self.scrollarea_fit_in, alignment=Qt.AlignHCenter)

        # -------------------

        self.scrollarea_fit_out = QScrollArea(self.tab_fit_out)
        self.scrollarea_fit_out.setMinimumWidth(805)
        self.scrollarea_fit_out.setMinimumHeight(505)

        self.table_fit_out = self.create_table_widget()

        self.scrollarea_fit_out.setWidget(self.table_fit_out)
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

    def stop_fit(self):
        if ConfirmDialog.confirmed(self, "Confirm STOP?"):
            self.stop_fit = True

    def do_fit(self):
        try:
            if not self.fit_global_parameters is None:
                self.fit_button.setEnabled(False)
                self.stop_fit = False

                congruence.checkStrictlyPositiveNumber(self.n_iterations, "Nr. Iterations")

                self.fit_global_parameters.set_n_max_iterations(self.n_iterations)
                self.fit_global_parameters.set_convergence_reached(False)
                self.fit_global_parameters.free_output_parameters.parse_formulas(self.free_output_parameters_text)

                initial_fit_global_parameters = self.fit_global_parameters.duplicate()

                if self.is_incremental == 1:
                    if self.current_iteration == 0:
                        self.fitter = FitterFactory.create_fitter(fitter_name=self.cb_fitter.currentText(),
                                                                  fitting_method=self.cb_fitting_method.currentText())

                        self.fitter.init_fitter(initial_fit_global_parameters)
                        self.current_wss = []
                        self.current_gof = []
                    else:
                        if len(initial_fit_global_parameters.get_parameters()) != len(self.fitter.fit_global_parameters.get_parameters()):
                            raise Exception("Incremental Fit is not possibile!\n\nParameters in the last fitting procedure are incompatible with the received ones")
                else:
                    self.fitter = FitterFactory.create_fitter(fitter_name=self.cb_fitter.currentText(),
                                                              fitting_method=self.cb_fitting_method.currentText())

                    self.fitter.init_fitter(initial_fit_global_parameters)
                    self.current_iteration = 0
                    self.current_wss = []
                    self.current_gof = []

                self.fitted_fit_global_parameters = initial_fit_global_parameters
                self.current_running_iteration = 0

                sys.stdout = EmittingStream(textWritten=self.write_stdout)

                try:
                    self.fit_thread = FitThread(self)
                    self.fit_thread.begin.connect(self.fit_begin)
                    self.fit_thread.update.connect(self.fit_update)
                    self.fit_thread.finished.connect(self.fit_completed)
                    self.fit_thread.start()
                except Exception as e:
                    raise FitNotStartedException(str(e))

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            sys.stdout = self.standard_ouput

            self.fit_button.setEnabled(True)

            if self.IS_DEVELOP: raise e

        self.setStatusMessage("")
        self.progressBarFinished()

    def send_current_fit(self):
        if not self.fit_global_parameters is None:
            self.send("Fit Global Parameters", self.fit_global_parameters.duplicate())

    def set_data(self, data):
        try:
            if not data is None:
                if self.is_incremental == 1 and not self.fit_global_parameters is None:
                    if not self.fit_global_parameters.is_compatibile(data):
                        QMessageBox.warning(self, "Incompatible Parameters",
                                             "Incremental Fit is not possibile!\n\nReceived parameters are incompatibile with the previous ones.\n" +
                                             "Only a new fit can be calculated (and previous results will be lost)",
                                             QMessageBox.Ok)

                        self.is_incremental = 0

                self.fit_global_parameters = data.duplicate()

                # keep existing text!
                existing_free_output_parameters = FreeOutputParameters()
                existing_free_output_parameters.parse_formulas(self.free_output_parameters_text)

                received_free_output_parameters = self.fit_global_parameters.free_output_parameters.duplicate()
                received_free_output_parameters.append(existing_free_output_parameters)

                self.text_area_free_out.setText(received_free_output_parameters.to_python_code())

                parameters = self.fit_global_parameters.free_input_parameters.as_parameters()
                parameters.extend(self.fit_global_parameters.get_parameters())

                self.populate_table(self.table_fit_in, parameters)

                self.tabs.setCurrentIndex(0)

                if self.fit_global_parameters.size_parameters is None:
                    self.tab_plot_size.setEnabled(False)
                    self.plot_size._backend.fig.set_facecolor("#D7DBDD")
                else:
                    self.tab_plot_size.setEnabled(True)
                    self.plot_size._backend.fig.set_facecolor("#FEFEFE")

                if self.fit_global_parameters.strain_parameters is None:
                    self.tab_plot_strain.setEnabled(False)
                    self.plot_strain._backend.fig.set_facecolor("#D7DBDD")
                else:
                    self.tab_plot_strain.setEnabled(True)
                    self.plot_strain._backend.fig.set_facecolor("#FEFEFE")

                if self.is_automatic_run:
                    self.do_fit()
        except Exception as e:
            QMessageBox.critical(self, "Error during load",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    def create_table_widget(self):
        table_fit = QTableWidget(1, 8)
        table_fit.setAlternatingRowColors(True)
        table_fit.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        table_fit.verticalHeader().setVisible(False)
        table_fit.setHorizontalHeaderLabels(self.horizontal_headers)

        table_fit.setColumnWidth(0, 200)
        table_fit.setColumnWidth(1, 120)
        table_fit.setColumnWidth(2, 120)
        table_fit.setColumnWidth(3, 120)
        table_fit.setColumnWidth(4, 60)
        table_fit.setColumnWidth(5, 60)
        table_fit.setColumnWidth(6, 250)
        table_fit.setColumnWidth(7, 120)

        table_fit.resizeRowsToContents()
        table_fit.setSelectionBehavior(QAbstractItemView.SelectRows)

        return table_fit

    def populate_table(self, table_widget, parameters):
        table_widget.clear()

        row_count = table_widget.rowCount()
        for n in range(0, row_count):
            table_widget.removeRow(0)

        for index in range(0, len(parameters)):
            table_widget.insertRow(0)

        for index in range(0, len(parameters)):
            change_color = not parameters[index].is_variable()
            color = QColor(167, 167, 167)

            table_item = QTableWidgetItem(parameters[index].parameter_name)
            table_item.setTextAlignment(Qt.AlignLeft)
            if change_color: table_item.setBackground(color)
            table_widget.setItem(index, 0, table_item)


            table_item = QTableWidgetItem(str(round(0.0 if parameters[index].value is None else parameters[index].value, 6)))
            table_item.setTextAlignment(Qt.AlignRight)
            if change_color: table_item.setBackground(color)
            table_widget.setItem(index, 1, table_item)


            if (not parameters[index].is_variable()) or parameters[index].boundary is None:
                table_item = QTableWidgetItem("")
                table_item.setTextAlignment(Qt.AlignRight)
                if change_color: table_item.setBackground(color)
                table_widget.setItem(index, 2, table_item)

                table_item = QTableWidgetItem("")
                table_item.setTextAlignment(Qt.AlignRight)
                if change_color: table_item.setBackground(color)
                table_widget.setItem(index, 3, table_item)
            else:
                if parameters[index].boundary.min_value == PARAM_HWMIN:
                    table_item = QTableWidgetItem("")
                    table_item.setTextAlignment(Qt.AlignRight)
                    if change_color: table_item.setBackground(color)
                    table_widget.setItem(index, 2, table_item)
                else:
                    table_item = QTableWidgetItem(str(round(0.0 if parameters[index].boundary.min_value is None else parameters[index].boundary.min_value, 6)))
                    table_item.setTextAlignment(Qt.AlignRight)
                    if change_color: table_item.setBackground(color)
                    table_widget.setItem(index, 2, table_item)

                if parameters[index].boundary.max_value == PARAM_HWMAX:
                    table_item = QTableWidgetItem("")
                    table_item.setTextAlignment(Qt.AlignRight)
                    if change_color: table_item.setBackground(color)
                    table_widget.setItem(index, 3, table_item)
                else:
                    table_item = QTableWidgetItem(str(round(0.0 if parameters[index].boundary.max_value is None else parameters[index].boundary.max_value, 6)))
                    table_item.setTextAlignment(Qt.AlignRight)
                    if change_color: table_item.setBackground(color)
                    table_widget.setItem(index, 3, table_item)

            table_item = QTableWidgetItem(str(parameters[index].fixed))
            table_item.setTextAlignment(Qt.AlignCenter)
            if change_color: table_item.setBackground(color)
            table_widget.setItem(index, 4, table_item)

            table_item = QTableWidgetItem(str(parameters[index].function))
            table_item.setTextAlignment(Qt.AlignCenter)
            if change_color: table_item.setBackground(color)
            table_widget.setItem(index, 5, table_item)

            if parameters[index].function:
                table_item = QTableWidgetItem(str(parameters[index].function_value))
                table_item.setTextAlignment(Qt.AlignLeft)
                if change_color: table_item.setBackground(color)
                table_widget.setItem(index, 6, table_item)
            else:
                table_item = QTableWidgetItem("")
                table_item.setTextAlignment(Qt.AlignLeft)
                if change_color: table_item.setBackground(color)
                table_widget.setItem(index, 6, table_item)

            table_item = QTableWidgetItem(str(round(0.0 if parameters[index].error is None else parameters[index].error, 6)))
            table_item.setTextAlignment(Qt.AlignRight)
            if change_color: table_item.setBackground(color)
            table_widget.setItem(index, 7, table_item)

        table_widget.setHorizontalHeaderLabels(self.horizontal_headers)
        table_widget.resizeRowsToContents()
        table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def save_data(self):
        try:
            if hasattr(self, "fitted_pattern") and not self.fitted_pattern is None:
                file_path = QFileDialog.getOpenFileName(self, "Select File", os.path.dirname(self.save_file_name))[0]

                if not file_path is None and not file_path.strip() == "":
                    self.save_file_name=file_path

                    text = "2Theta [deg], s [Å-1], Intensity, Fit, Residual"

                    for index in range(0, self.fitted_pattern.diffraction_points_count()):
                        text += "\n" + str(self.fitted_pattern.get_diffraction_point(index).twotheta) + "  " + \
                                str(self.fitted_pattern.get_diffraction_point(index).s) + " " + \
                                str(self.fit_global_parameters.fit_initialization.diffraction_pattern.get_diffraction_point(index).intensity) + " " + \
                                str(self.fitted_pattern.get_diffraction_point(index).intensity) + " " + \
                                str(self.fitted_pattern.get_diffraction_point(index).error) + " "

                    file = open(self.save_file_name, "w")
                    file.write(text)
                    file.flush()
                    file.close()

                    QMessageBox.information(self,
                                            "Save Data",
                                            "Fitted data saved on file:\n" + self.save_file_name,
                                            QMessageBox.Ok)
        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    def show_data(self):
        diffraction_pattern = self.fitted_fit_global_parameters.fit_initialization.diffraction_pattern

        x = []
        y = []
        yf = []
        res = []

        for index in range(0, self.fitted_pattern.diffraction_points_count()):
            x.append(diffraction_pattern.get_diffraction_point(index).twotheta)
            y.append(diffraction_pattern.get_diffraction_point(index).intensity)
            yf.append(self.fitted_pattern.get_diffraction_point(index).intensity)
            res.append(self.fitted_pattern.get_diffraction_point(index).error)

        res = -10 + (res-numpy.max(res))

        self.plot_fit.addCurve(x, y, legend="data", linewidth=4, color="blue")
        self.plot_fit.addCurve(x, yf, legend="fit", color="red")
        self.plot_fit.addCurve(x, res, legend="residual", color="#2D811B")

        if not self.fit_data is None:
            x = numpy.arange(1, self.current_iteration + 1)
            self.current_wss.append(self.fit_data.wss)
            self.current_gof.append(self.fit_data.gof())

            self.plot_fit_wss.addCurve(x, self.current_wss, legend="wss", symbol='o', color="blue")
            self.plot_fit_gof.addCurve(x, self.current_gof, legend="gof", symbol='o', color="red")

        if not self.fitted_fit_global_parameters.size_parameters is None:
            x, y = self.fitted_fit_global_parameters.size_parameters.get_distribution()

            self.plot_size.addCurve(x, y, legend="distribution", color="blue")

        if not self.fitted_fit_global_parameters.strain_parameters is None:
            x, y = self.fitted_fit_global_parameters.strain_parameters.get_warren_plot(1, 0, 0)
            self.plot_strain.addCurve(x, y, legend="h00", color='blue')
            x, y = self.fitted_fit_global_parameters.strain_parameters.get_warren_plot(1, 1, 1)
            self.plot_strain.addCurve(x, y, legend="hhh", color='red')
            x, y = self.fitted_fit_global_parameters.strain_parameters.get_warren_plot(1, 1, 0)
            self.plot_strain.addCurve(x, y, legend="hh0", color='green')

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

        self.fit_thread.mutex.tryLock()

        try:
            self.current_iteration += 1
            self.current_running_iteration += 1

            self.progressBarSet(int(self.current_running_iteration*100/self.n_iterations))
            self.setStatusMessage("Fit iteration nr. " + str(self.current_iteration) + "/" + str(self.n_iterations) + " completed")

            self.show_data()

            parameters = self.fitted_fit_global_parameters.free_input_parameters.as_parameters()
            parameters.extend(self.fitted_fit_global_parameters.get_parameters())
            parameters.extend(self.fitted_fit_global_parameters.free_output_parameters.as_parameters())

            self.populate_table(self.table_fit_out, parameters)

            if self.current_iteration == 1:
                self.tabs.setCurrentIndex(1)
                self.tabs_plot.setCurrentIndex(0)

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

        self.fit_thread.mutex.unlock()


    def fit_completed(self):
        sys.stdout = self.standard_output

        self.setStatusMessage("Fitting procedure completed")

        if self.is_incremental == 1:
            self.fit_global_parameters = self.fitted_fit_global_parameters.duplicate()

            parameters = self.fit_global_parameters.free_input_parameters.as_parameters()
            parameters.extend(self.fit_global_parameters.get_parameters())

            self.populate_table(self.table_fit_in, parameters)

        self.send("Fit Global Parameters", self.fitted_fit_global_parameters)

        self.fit_button.setEnabled(True)
        self.stop_fit = False
        self.progressBarFinished()

from PyQt5.QtCore import QThread, pyqtSignal

class FitThread(QThread):

    begin = pyqtSignal()
    update = pyqtSignal()
    mutex = QMutex()

    DEBUG = False

    def __init__(self, fitter_widget):
        super(FitThread, self).__init__(fitter_widget)
        self.fitter_widget = fitter_widget

    def run(self):
        try:
            self.begin.emit()

            for iteration in range(1, self.fitter_widget.n_iterations + 1):
                if self.fitter_widget.stop_fit: break

                self.fitter_widget.fitted_pattern, \
                self.fitter_widget.fitted_fit_global_parameters, \
                self.fitter_widget.fit_data = \
                    self.fitter_widget.fitter.do_fit(current_fit_global_parameters=self.fitter_widget.fitted_fit_global_parameters,
                                                     current_iteration=iteration)

                self.update.emit()

                if self.fitter_widget.stop_fit: break
                if self.fitter_widget.fitted_fit_global_parameters.is_convergence_reached(): break
        except Exception as e:
            QMessageBox.critical(self.fitter_widget, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            self.finished.emit()

            if self.fitter_widget.DEBUG: raise e

class FitNotStartedException(Exception):
    def __init__(self, *args, **kwargs): # real signature unknown
        super(FitNotStartedException, self).__init__(args, kwargs)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWFitter()
    ow.show()
    a.exec_()
    ow.saveSettings()
