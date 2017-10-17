from Orange.widgets import widget

from Orange.widgets import gui
from Orange.data import Table

class OWProva(widget.OWWidget):
    name = "Prova"
    description = "Fazo na prova"
    icon = "icons/prova.jpg"
    priority = 1

    inputs = [("XRD Data", Table, 'set_data')]
    #outputs = [("Data", Orange.data.Table)]

    input_data = None

    want_main_area = True

    def __init__(self):
        super().__init__()

    def set_data(self, data):
        self.input_data = data

        print("DIO SATANASSO")