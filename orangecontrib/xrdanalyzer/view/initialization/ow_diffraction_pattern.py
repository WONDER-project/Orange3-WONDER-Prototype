import os, sys, numpy

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

from silx.gui.plot.PlotWindow import PlotWindow

from Orange.widgets.settings import Setting
from Orange.widgets import gui as orangegui

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.model.diffraction_pattern import DiffractionPattern, DiffractionPatternFactory, DiffractionPatternLimits
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
    wavelength_fixed = Setting(0)
    wavelength_has_min = Setting(0)
    wavelength_min = Setting(0.0)
    wavelength_has_max = Setting(0)
    wavelength_max = Setting(0.0)
    wavelength_function = Setting(0)
    wavelength_function_value = Setting("")

    diffraction_pattern = None

    twotheta_min = Setting(0.0)
    twotheta_has_min = Setting(0)

    twotheta_max = Setting(0.0)
    twotheta_has_max = Setting(0)

    horizontal_headers = ["2Theta [deg]", "s [nm^-1]", "Intensity", "Error"]

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

        box = gui.widgetBox(main_box, "", orientation="horizontal", width=self.CONTROL_AREA_WIDTH - 25)

        orangegui.checkBox(box, self, "twotheta_has_min", "2th min [deg]", labelWidth=350)
        gui.lineEdit(box, self, "twotheta_min", "", labelWidth=5, valueType=float, validator=QDoubleValidator())

        box = gui.widgetBox(main_box, "", orientation="horizontal", width=self.CONTROL_AREA_WIDTH - 25)

        orangegui.checkBox(box, self, "twotheta_has_max", "2th max [deg]", labelWidth=350)
        gui.lineEdit(box, self, "twotheta_max", "", labelWidth=5, valueType=float, validator=QDoubleValidator())

        orangegui.separator(main_box)

        self.create_box(main_box,  "wavelength", label="\u03BB  [nm]", disable_function=True)

        orangegui.separator(main_box)

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

        self.table_data = self.create_table_widget()

        self.scrollarea.setWidget(self.table_data)
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

            if self.twotheta_has_min == 1 or self.twotheta_has_max == 1:
                limits = DiffractionPatternLimits(twotheta_min=self.twotheta_min if self.twotheta_has_min==1 else -numpy.inf,
                                                  twotheta_max=self.twotheta_max if self.twotheta_has_max==1 else numpy.inf)
            else:
                limits=None

            self.diffraction_pattern = DiffractionPatternFactory.create_diffraction_pattern_from_file(self.filename,
                                                                                                      self.populate_parameter("wavelength", DiffractionPattern.get_parameters_prefix()),
                                                                                                      limits)

            self.wavelength = self.diffraction_pattern.wavelength.value

            self.show_data()

            self.tabs.setCurrentIndex(1)

            self.send("Fit Global Parameters", FitGlobalParameters(fit_initialization=FitInitialization(diffraction_pattern=self.diffraction_pattern)))

        except Exception as e:
            QMessageBox.critical(self, "Error during load",
                                 str(e),
                                 QMessageBox.Ok)

            if self.IS_DEVELOP: raise e

    def show_data(self):
        x = []
        y = []

        for index in range(0, self.diffraction_pattern.diffraction_points_count()):
            x.append(self.diffraction_pattern.get_diffraction_point(index).twotheta)
            y.append(self.diffraction_pattern.get_diffraction_point(index).intensity)

        self.plot.addCurve(x, y, linewidth=2, color="#0B0B61")

        self.populate_table(self.table_data, self.diffraction_pattern)


    def create_table_widget(self):
        table = QTableWidget(1, 4)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        table.verticalHeader().setVisible(False)
        table.setHorizontalHeaderLabels(self.horizontal_headers)

        table.setColumnWidth(0, 80)
        table.setColumnWidth(1, 80)
        table.setColumnWidth(2, 80)
        table.setColumnWidth(3, 80)

        table.resizeRowsToContents()
        table.setSelectionBehavior(QAbstractItemView.SelectRows)

        return table

    def populate_table(self, table_widget, diffraction_pattern):
        table_widget.clear()

        row_count = table_widget.rowCount()
        for n in range(0, row_count):
            table_widget.removeRow(0)

        for index in range(0, self.diffraction_pattern.diffraction_points_count()):
            table_widget.insertRow(0)

        for index in range(0, self.diffraction_pattern.diffraction_points_count()):

            table_item = QTableWidgetItem(str(round(self.diffraction_pattern.get_diffraction_point(index).twotheta, 6)))
            table_item.setTextAlignment(Qt.AlignRight)
            table_widget.setItem(index, 0, table_item)

            table_item = QTableWidgetItem(str(round(self.diffraction_pattern.get_diffraction_point(index).s, 6)))
            table_item.setTextAlignment(Qt.AlignRight)
            table_widget.setItem(index, 1, table_item)

            table_item = QTableWidgetItem(str(round(self.diffraction_pattern.get_diffraction_point(index).intensity, 6)))
            table_item.setTextAlignment(Qt.AlignRight)
            table_widget.setItem(index, 2, table_item)

            table_item = QTableWidgetItem(str(round(0.0 if self.diffraction_pattern.get_diffraction_point(index).error is None else self.diffraction_pattern.get_diffraction_point(index).error, 6)))
            table_item.setTextAlignment(Qt.AlignRight)
            table_widget.setItem(index, 3, table_item)

        table_widget.setHorizontalHeaderLabels(self.horizontal_headers)
        table_widget.resizeRowsToContents()
        table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)



if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWDiffractionPattern()
    ow.show()
    a.exec_()
    ow.saveSettings()
