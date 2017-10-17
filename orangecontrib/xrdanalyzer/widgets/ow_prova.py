import numpy

from Orange.widgets import widget

from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.data import Table

from PyQt5.QtWidgets import QApplication, QTextEdit, QMessageBox
from PyQt5.QtCore import QRect, Qt

from silx.gui.plot.PlotWindow import PlotWindow

class OWProva(widget.OWWidget):
    name = "Prova"
    description = "Fazo na prova"
    icon = "icons/prova.png"
    priority = 1

    inputs = [("XRD Data", Table, 'set_data')]
    outputs = [("Data", Table)]

    input_data = None

    want_main_area = True

    MAX_WIDTH = 1320
    MAX_HEIGHT = 700
    CONTROL_AREA_WIDTH = 405

    is_automatic_load = Setting(1)

    def __init__(self):
        super().__init__()

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width()*0.05),
                               round(geom.height()*0.05),
                               round(min(geom.width()*0.98, self.MAX_WIDTH)),
                               round(min(geom.height()*0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        self.general_options_box = gui.widgetBox(self.controlArea, "General Options", addSpace=False, orientation="vertical")

        gui.checkBox(self.general_options_box, self, "is_automatic_load", "Automatic Load")

        button = gui.button(self.general_options_box, self, "Show Data", width=200, height=50, callback=self.show_data)
        button.setStyleSheet("color: black;")


        self.tabs = gui.tabWidget(self.mainArea)

        self.tab_data = gui.createTabPage(self.tabs, "Data")
        self.tab_plot = gui.createTabPage(self.tabs, "Plot")

        self.plot = PlotWindow()
        self.plot.setDefaultPlotLines(True)
        self.plot.setActiveCurveColor(color="#00008B")
        self.plot.setGraphXLabel("2Theta")
        self.plot.setGraphYLabel("Counts")

        self.tab_plot.layout().addWidget(self.plot)

        self.text_area = self.textArea(height=600, width=700)

        self.tab_data.layout().addWidget(self.text_area)

    def set_data(self, data):
        self.input_data = data

        if self.is_automatic_load: self.show_data()

    def show_data(self):
        if self.input_data is None:
            QMessageBox.critical(self, "Error",
                                       "Input data is Empty", QMessageBox.Ok)

        text = "2Theta        Counts"

        x = []
        y = []

        for index in range(0, len(self.input_data.X)):
            text += "\n" + str(self.input_data.X[index][1]) + "  " + str(self.input_data.X[index][2])
            x.append(self.input_data.X[index][1])
            y.append(self.input_data.X[index][2])

        self.text_area.setText(text)

        self.plot.addCurve(x, y)

        # Esempio di post-elaborazione prima di restituire il risultato

        rows = numpy.zeros((len(x), 2))

        rows[:, 0] = numpy.array(x)
        rows[:, 1] = numpy.array(y) * 1000

        output_table = Table.from_numpy(domain=None, X=rows)

        self.send("Data", output_table)

    def textArea(self, height=None, width=None, readOnly=True):
        area = QTextEdit()
        area.setReadOnly(readOnly)
        area.setStyleSheet("background-color: white;")

        if not height is None: area.setFixedHeight(height)
        if not width is None: area.setFixedWidth(width)

        return area