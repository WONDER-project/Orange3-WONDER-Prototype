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


from orangecontrib.xrdanalyzer.controller.fit.fitter_factory import FitterFactory, FitterName

try:
    import orangecontrib.xrdanalyzer.util.test_recovery
    is_recovery = False
except:
    is_recovery = True

if not is_recovery:
    from orangecontrib.xrdanalyzer.util import congruence
    from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import PARAM_HWMAX, PARAM_HWMIN
    from orangecontrib.xrdanalyzer.controller.fit.fit_global_parameters import FitGlobalParameters, FreeOutputParameters
    from orangecontrib.xrdanalyzer.controller.fit.init.thermal_polarization_parameters import ThermalPolarizationParameters
else:
    from orangecontrib.xrdanalyzer.recovery.util import congruence
    from orangecontrib.xrdanalyzer.recovery.controller.fit.fit_parameter import PARAM_HWMAX, PARAM_HWMIN
    from orangecontrib.xrdanalyzer.recovery.controller.fit.fit_global_parameters import FitGlobalParameters, FreeOutputParameters
    from orangecontrib.xrdanalyzer.recovery.controller.fit.init.thermal_polarization_parameters import ThermalPolarizationParameters


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

    is_interactive = Setting(1)

    horizontal_headers = ["Name", "Value", "Min", "Max", "Fixed", "Function", "Expression", "Var"]

    inputs = [("Fit Global Parameters", FitGlobalParameters, 'set_data')]
    outputs = [("Fit Global Parameters", FitGlobalParameters)]

    fit_global_parameters = None
    fitted_fit_global_parameters = None
    current_wss = []
    current_gof = []

    stop_fit = False
    fit_running = False

    thread_exception = None

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

        self.cb_interactive = orangegui.comboBox(iteration_box, self, "is_interactive", label="Refresh Plots while fitting", items=["No", "Yes"], orientation="horizontal")

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
        self.std_output.setStyleSheet("font-family: Courier, monospace;")

        out_box = gui.widgetBox(self.mainArea, "System Output", addSpace=False, orientation="horizontal")
        out_box.layout().addWidget(self.std_output)

        self.tabs_plot_fit = gui.tabWidget(self.tab_plot_fit)

        self.tab_plot_fit_data = gui.createTabPage(self.tabs_plot_fit, "Data")
        self.tab_plot_fit_wss  = gui.createTabPage(self.tabs_plot_fit, "W.S.S.")
        self.tab_plot_fit_gof  = gui.createTabPage(self.tabs_plot_fit, "G.o.F.")

        self.tabs_plot_fit_data = gui.tabWidget(self.tab_plot_fit_data)

        self.build_plot_fit()

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

    def build_plot_fit(self):
        fit_global_parameter = self.fit_global_parameters if self.fitted_fit_global_parameters is None else self.fitted_fit_global_parameters

        self.plot_fit = []
        self.tabs_plot_fit_data.clear()

        for index in range(1 if fit_global_parameter is None else len(fit_global_parameter.fit_initialization.diffraction_patterns)):
            tab_plot_fit_data = gui.createTabPage(self.tabs_plot_fit_data, "Diff. Patt. " + str(index+1))

            plot_fit = PlotWindow()
            plot_fit.setDefaultPlotLines(True)
            plot_fit.setActiveCurveColor(color="#00008B")
            plot_fit.setGraphXLabel(r"2$\theta$")
            plot_fit.setGraphYLabel("Intensity")

            self.plot_fit.append(plot_fit)
            tab_plot_fit_data.layout().addWidget(plot_fit)

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
                self.cb_interactive.setEnabled(False)

                self.stop_fit = False

                congruence.checkStrictlyPositiveNumber(self.n_iterations, "Nr. Iterations")

                if self.fit_global_parameters.fit_initialization is None:
                    raise ValueError("Mandatory widgets (Load Data/Fit Initialization/Crystal Structure) are totally missing.")

                if self.fit_global_parameters.fit_initialization.fft_parameters is None:
                    raise ValueError("FFT parameters is missing: add the proper widget before the Fitter")

                if self.fit_global_parameters.fit_initialization.diffraction_patterns is None:
                    raise ValueError("Diffraction Pattern is missing: add the proper widget before the Fitter")

                if self.fit_global_parameters.fit_initialization.crystal_structures is None:
                    raise ValueError("Crystal Structure is missing: add the proper widget before the Fitter")

                self.fit_global_parameters.set_n_max_iterations(self.n_iterations)
                self.fit_global_parameters.set_convergence_reached(False)
                self.fit_global_parameters.free_output_parameters.parse_formulas(self.free_output_parameters_text)

                initial_fit_global_parameters = self.fit_global_parameters.duplicate()

                if self.is_incremental == 1 and self.current_iteration > 0:
                    if len(initial_fit_global_parameters.get_parameters()) != len(self.fitter.fit_global_parameters.get_parameters()):
                        raise Exception("Incremental Fit is not possibile!\n\nParameters in the last fitting procedure are incompatible with the received ones")

                sys.stdout = EmittingStream(textWritten=self.write_stdout)

                if self.is_incremental == 0 or (self.is_incremental == 1 and self.current_iteration == 0):
                    self.fitter = FitterFactory.create_fitter(fitter_name=self.cb_fitter.currentText(),
                                                              fitting_method=self.cb_fitting_method.currentText())

                    self.fitter.init_fitter(initial_fit_global_parameters)
                    self.current_wss = []
                    self.current_gof = []
                    self.current_iteration = 0 if self.is_incremental == 0 else self.current_iteration

                self.fitted_fit_global_parameters = initial_fit_global_parameters
                self.current_running_iteration = 0

                try:
                    self.fit_thread = FitThread(self)
                    self.fit_thread.begin.connect(self.fit_begin)
                    self.fit_thread.update.connect(self.fit_update)
                    self.fit_thread.finished.connect(self.fit_completed)
                    self.fit_thread.error.connect(self.fit_error)
                    self.fit_thread.start()
                except Exception as e:
                    raise FitNotStartedException(str(e))

        except Exception as e:
            QMessageBox.critical(self, "Error",
                                 str(e),
                                 QMessageBox.Ok)

            sys.stdout = self.standard_ouput

            self.fit_button.setEnabled(True)
            self.cb_interactive.setEnabled(True)

            if self.IS_DEVELOP: raise e

        self.setStatusMessage("")
        self.progressBarFinished()

    def send_current_fit(self):
        if not self.fit_global_parameters is None:
            self.send("Fit Global Parameters", self.fit_global_parameters.duplicate())

    def set_data(self, data):
        try:
            if not data is None:
                if self.fit_running: raise RuntimeError("Fit is Running: Input data are not accepted!")

                if self.is_incremental == 1 and not self.fit_global_parameters is None:
                    if not ConfirmDialog.confirmed(self, message="Warning: Fitter is in set in incremental mode, but received fit parameters will replace the already fitted ones. Do you accept them?"):
                        return

                self.current_iteration = 0

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

                if self.is_incremental == 0 or (self.is_incremental == 1 and self.current_iteration == 0):
                    sys.stdout = EmittingStream(textWritten=self.write_stdout)

                    self.fitted_fit_global_parameters = self.fit_global_parameters.duplicate()
                    self.fitted_fit_global_parameters.evaluate_functions()

                    self.fitter = FitterFactory.create_fitter(fitter_name=self.cb_fitter.currentText(),
                                                              fitting_method=self.cb_fitting_method.currentText())
                    self.fitter.init_fitter(self.fitted_fit_global_parameters)

                    self.fitted_patterns = self.fitter.build_fitted_diffraction_pattern(self.fitted_fit_global_parameters)
                    self.fit_data = None

                    self.show_data(is_init=True)

                    self.tabs.setCurrentIndex(1)
                    self.tabs_plot.setCurrentIndex(0)

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


    def add_table_item(self, 
                       table_widget, 
                       row_index, 
                       column_index,
                       text="",
                       alignement=Qt.AlignLeft,
                       change_color=False,
                       color=QColor(255, 255, 255)):

            table_item = QTableWidgetItem(text)
            table_item.setTextAlignment(alignement)
            if change_color: table_item.setBackground(color)
            table_widget.setItem(row_index, column_index, table_item)

    def analyze_parameter(self, parameter):
        if parameter.parameter_name == ThermalPolarizationParameters.get_parameters_prefix() + "debye_waller_factor":
            parameter = parameter.duplicate()
            parameter.rescale(100) # from nm-2 to A-2

        return parameter

    def populate_table(self, table_widget, parameters):
        table_widget.clear()

        row_count = table_widget.rowCount()
        for n in range(0, row_count):
            table_widget.removeRow(0)

        for index in range(0, len(parameters)):
            table_widget.insertRow(0)

        for index in range(0, len(parameters)):
            parameter = parameters[index]
            parameter = self.analyze_parameter(parameter)
            change_color = not parameter.is_variable()

            if change_color:
                if parameter.input_parameter: color = QColor(213, 245, 227)
                elif parameter.fixed: color = QColor(190, 190, 190)
                elif parameter.output_parameter: color = QColor(242, 245, 169)
                else: color = QColor(169, 208, 245)
            else:
                color = None
  
            self.add_table_item(table_widget, index, 0,
                                parameter.parameter_name,
                                Qt.AlignLeft, change_color, color)

            self.add_table_item(table_widget, index, 1,
                                str(round(0.0 if parameter.value is None else parameter.value, 6)),
                                Qt.AlignRight, change_color, color)

            if (not parameter.is_variable()) or parameter.boundary is None: text_2 = text_3 = ""
            else:
                if parameter.boundary.min_value == PARAM_HWMIN: text_2 = ""
                else: text_2 = str(round(0.0 if parameter.boundary.min_value is None else parameter.boundary.min_value, 6))

                if parameter.boundary.max_value == PARAM_HWMAX: text_3 = ""
                else: text_3 = str(round(0.0 if parameter.boundary.max_value is None else parameter.boundary.max_value, 6))

            self.add_table_item(table_widget, index, 2,
                                text_2,
                                Qt.AlignRight, change_color, color)
            self.add_table_item(table_widget, index, 3,
                                text_3,
                                Qt.AlignRight, change_color, color)

            self.add_table_item(table_widget, index, 4,
                                str(parameter.fixed),
                                Qt.AlignCenter, change_color, color)
            self.add_table_item(table_widget, index, 5,
                                str(parameter.function),
                                Qt.AlignCenter, change_color, color)

            if parameter.function: text_6 = str(parameter.function_value)
            else: text_6 = ""

            self.add_table_item(table_widget, index, 6,
                                text_6,
                                Qt.AlignLeft, change_color, color)

            self.add_table_item(table_widget, index, 7,
                                str(round(0.0 if parameter.error is None else parameter.error, 6)),
                                Qt.AlignRight, change_color, color)

        table_widget.setHorizontalHeaderLabels(self.horizontal_headers)
        table_widget.resizeRowsToContents()
        table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def save_data(self):
        try:
            if hasattr(self, "fitted_patterns") and not self.fitted_patterns is None:
                file_path = QFileDialog.getSaveFileName(self, "Select File", os.path.dirname(self.save_file_name))[0]

                if not file_path is None and not file_path.strip() == "":
                    self.save_file_name=file_path

                    text = ""
                    for diffraction_pattern_index in range(len(self.fitted_patterns)):
                        fitted_pattern = self.fitted_patterns[diffraction_pattern_index]
                        diffraction_pattern = self.fit_global_parameters.fit_initialization.diffraction_patterns[diffraction_pattern_index]

                        text += "" if diffraction_pattern_index==0 else "\n"
                        text += "------------------------------------------------------------------------\n"
                        text +="DIFFRACTION PATTERN Nr. " + str(diffraction_pattern_index+1) + "\n\n"
                        text += "2Theta [deg], s [Å-1], Intensity, Fit, Residual\n"
                        text += "------------------------------------------------------------------------"

                        for index in range(0, fitted_pattern.diffraction_points_count()):
                            text += "\n" + str(fitted_pattern.get_diffraction_point(index).twotheta) + "  " + \
                                    str(fitted_pattern.get_diffraction_point(index).s) + " " + \
                                    str(diffraction_pattern.get_diffraction_point(index).intensity) + " " + \
                                    str(fitted_pattern.get_diffraction_point(index).intensity) + " " + \
                                    str(fitted_pattern.get_diffraction_point(index).error) + " "

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

    def show_data(self, is_init=False):
        diffraction_pattern_number = len(self.fitted_fit_global_parameters.fit_initialization.diffraction_patterns)

        if is_init:
            self.build_plot_fit()
            self.x = [None]*diffraction_pattern_number
            self.y = [None]*diffraction_pattern_number

        for diffraction_pattern_index in range(diffraction_pattern_number):
            diffraction_pattern = self.fitted_fit_global_parameters.fit_initialization.diffraction_patterns[diffraction_pattern_index]
            fitted_pattern = self.fitted_patterns[diffraction_pattern_index]

            if is_init:
                x = []
                y = []
                yf = []
                res = []

                for index in range(0, fitted_pattern.diffraction_points_count()):
                    x.append(diffraction_pattern.get_diffraction_point(index).twotheta)
                    y.append(diffraction_pattern.get_diffraction_point(index).intensity)
                    yf.append(fitted_pattern.get_diffraction_point(index).intensity)
                    res.append(fitted_pattern.get_diffraction_point(index).error)

                self.x[diffraction_pattern_index] = x
                self.y[diffraction_pattern_index] = y
            else:
                yf = []
                res = []

                for index in range(0, fitted_pattern.diffraction_points_count()):
                    yf.append(fitted_pattern.get_diffraction_point(index).intensity)
                    res.append(fitted_pattern.get_diffraction_point(index).error)

            res = -10 + (res-numpy.max(res))

            if is_init: self.plot_fit[diffraction_pattern_index].addCurve(self.x[diffraction_pattern_index], self.y[diffraction_pattern_index], legend="data", linewidth=4, color="blue")
            self.plot_fit[diffraction_pattern_index].addCurve(self.x[diffraction_pattern_index], yf, legend="fit", color="red")
            self.plot_fit[diffraction_pattern_index].addCurve(self.x[diffraction_pattern_index], res, legend="residual", color="#2D811B")

        if not self.fit_data is None and self.is_interactive == 1:
            x = numpy.arange(1, self.current_iteration + 1)
            self.current_wss.append(self.fit_data.wss)
            self.current_gof.append(self.fit_data.gof())

            self.plot_fit_wss.addCurve(x, self.current_wss, legend="wss", symbol='o', color="blue")
            self.plot_fit_gof.addCurve(x, self.current_gof, legend="gof", symbol='o', color="red")

        if not self.fitted_fit_global_parameters.size_parameters is None:
            if self.current_iteration <= 1: #TO BE SURE...
                x, y, self.D_max = self.fitted_fit_global_parameters.size_parameters[0].get_distribution()
            else:
                x, y, self.D_max = self.fitted_fit_global_parameters.size_parameters[0].get_distribution(auto=False, D_max=self.D_max)

            self.plot_size.addCurve(x, y, legend="distribution", color="blue")

        if not self.fitted_fit_global_parameters.strain_parameters is None:
            x, y = self.fitted_fit_global_parameters.strain_parameters[0].get_warren_plot(1, 0, 0, L_max=self.D_max)
            self.plot_strain.addCurve(x, y, legend="h00", color='blue')
            x, y = self.fitted_fit_global_parameters.strain_parameters[0].get_warren_plot(1, 1, 1, L_max=self.D_max)
            self.plot_strain.addCurve(x, y, legend="hhh", color='red')
            x, y = self.fitted_fit_global_parameters.strain_parameters[0].get_warren_plot(1, 1, 0, L_max=self.D_max)
            self.plot_strain.addCurve(x, y, legend="hh0", color='green')

##########################################
# THREADING
##########################################
    def fit_begin(self):
        from PyQt5.QtCore import QMutex

        self.fit_thread.mutex.tryLock()

        self.progressBarInit()
        self.setStatusMessage("Fitting procedure started")
        print("Fitting procedure started")
        self.fit_running = True

        self.fit_thread.mutex.unlock()

    def fit_update(self):

        self.fit_thread.mutex.tryLock()

        try:
            self.current_iteration += 1
            self.current_running_iteration += 1

            self.progressBarSet(int(self.current_running_iteration*100/self.n_iterations))
            self.setStatusMessage("Fit iteration nr. " + str(self.current_iteration) + "/" + str(self.n_iterations) + " completed")
            print("Fit iteration nr. " + str(self.current_iteration) + "/" + str(self.n_iterations) + " completed")

            if self.is_interactive == 1:
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

            if self.IS_DEVELOP: raise e

        self.fit_thread.mutex.unlock()


    def fit_completed(self):
        sys.stdout = self.standard_output

        self.setStatusMessage("Fitting procedure completed")
        print("Fitting procedure completed")

        if self.is_incremental == 1:
            self.fit_global_parameters = self.fitted_fit_global_parameters.duplicate()

            parameters = self.fit_global_parameters.free_input_parameters.as_parameters()
            parameters.extend(self.fit_global_parameters.get_parameters())

            self.populate_table(self.table_fit_in, parameters)

        if self.is_interactive == 0:
            self.show_data()

            parameters = self.fitted_fit_global_parameters.free_input_parameters.as_parameters()
            parameters.extend(self.fitted_fit_global_parameters.get_parameters())
            parameters.extend(self.fitted_fit_global_parameters.free_output_parameters.as_parameters())

            self.populate_table(self.table_fit_out, parameters)

            if self.current_iteration == 1:
                self.tabs.setCurrentIndex(1)
                self.tabs_plot.setCurrentIndex(0)

        self.send("Fit Global Parameters", self.fitted_fit_global_parameters)

        self.fit_button.setEnabled(True)
        self.cb_interactive.setEnabled(True)
        self.fit_running = False
        self.stop_fit = False
        self.progressBarFinished()

    def fit_error(self):
        QMessageBox.critical(self, "Error",
                             "Fit Failed: " + str(self.thread_exception),
                             QMessageBox.Ok)

        self.fit_completed()

        if self.IS_DEVELOP: raise self.thread_exception

from PyQt5.QtCore import QThread, pyqtSignal

class FitThread(QThread):

    begin = pyqtSignal()
    update = pyqtSignal()
    error = pyqtSignal()
    mutex = QMutex()

    def __init__(self, fitter_widget):
        super(FitThread, self).__init__(fitter_widget)
        self.fitter_widget = fitter_widget

    def run(self):
        try:
            self.begin.emit()

            for iteration in range(1, self.fitter_widget.n_iterations + 1):
                if self.fitter_widget.stop_fit: break

                self.fitter_widget.fitted_patterns, \
                self.fitter_widget.fitted_fit_global_parameters, \
                self.fitter_widget.fit_data = \
                    self.fitter_widget.fitter.do_fit(current_fit_global_parameters=self.fitter_widget.fitted_fit_global_parameters,
                                                     current_iteration=iteration)

                self.update.emit()

                if self.fitter_widget.stop_fit: break
                if self.fitter_widget.fitted_fit_global_parameters.is_convergence_reached(): break
        except Exception as exception:
            self.fitter_widget.thread_exception = exception

            self.error.emit()

class FitNotStartedException(Exception):
    def __init__(self, *args, **kwargs): # real signature unknown
        super(FitNotStartedException, self).__init__(args, kwargs)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWFitter()
    ow.show()
    a.exec_()
    ow.saveSettings()
