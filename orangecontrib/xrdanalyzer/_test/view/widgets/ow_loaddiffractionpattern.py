import os

from PyQt5.QtWidgets import QMessageBox, QScrollArea, QTableWidget
from silx.gui.plot.PlotWindow import PlotWindow

from Orange.widgets.settings import Setting

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.model.diffractionpattern import DiffractionPattern, DiffractionPatternFactory
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui
from orangecontrib.xrdanalyzer.util import congruence

class OWLoaddiffractionpattern(OWGenericWidget):

    name = "Load diffraction pattern"
    description = "Loads diffraction pattern " \
                  "points from most common file formats"
    icon = "icons/loaddiffpattern.png"
    priority = 60

    want_main_area = True

    filename = Setting("<input file>")
    diffraction_pattern = None

    outputs = [("Diffractionpattern", DiffractionPattern)]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea,
                                 "Load diffraction pattern", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 5, height=600)
        self.le_filename = gui.lineEdit(main_box,
                                        self,
                                        value="filename",
                                        valueType=str,
                                        label="File",
                                        labelWidth=50)

        gui.button(main_box, self, "...", width=40,
                         callback=self.open_folders)

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
        self.scrollarea.setMinimumWidth(self.CONTROL_AREA_WIDTH - 35)
        #table_box.layout().addWidget(self.scrollarea, alignment=Qt.AlignHCenter)



    def open_folders(self):
        self.filename=gui.selectFileFromDialog(self,
                                               self.filename,
                                               start_directory=os.curdir)

        self.le_filename.setText(self.filename)
        self.loaddiffractionpattern()
        self.show_data()

    def loaddiffractionpattern(self):
        try:
            congruence.checkFile(self.filename)

            self.diffraction_pattern = DiffractionPatternFactory.create_diffraction_pattern_from_file(self.filename)

            self.send("Diffractionpattern", self.diffraction_pattern)

        except Exception as e:
            QMessageBox.critical(self, "Input Error",
                                 str(e),
                                 QMessageBox.Ok)

    def show_data(self):
        x = []
        y = []
        for index in range(0, self.diffraction_pattern.diffraction_points_count()):
            x.append(self.diffraction_pattern.get_diffraction_point(index).twotheta)
            y.append(self.diffraction_pattern.get_diffraction_point(index).intensity)

        self.plot.addCurve(x, y)


