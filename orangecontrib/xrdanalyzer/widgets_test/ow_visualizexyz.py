

from PyQt5.QtWidgets import QTextEdit

from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui
from orangecontrib.xrdanalyzer.model.atom import  AtomList

class OWVisualizexyz(OWGenericWidget):

    name = "Visualize xyz"
    description = "Visualize the result of loading an xyz file"
    icon = "icons/visualizexyz.png"
    priority = 51

    want_main_area = True
    atom_list = None

    inputs = [("Atomlist", AtomList, "set_data")]

    def __init__(self):
        super().__init__(show_automatic_box=True)

        main_box = gui.widgetBox(self.controlArea, "Load xyz file", orientation="vertical",
                                 width=self.CONTROL_AREA_WIDTH - 5, height=600)

        gui.button(main_box, self, "Show Data", width=185, height=50, callback=self.show_data)

        show_box = gui.widgetBox(self.mainArea, "the file is:", orientation="vertical")

        self.text_area = gui.textArea(height=600, width=700)

        show_box.layout().addWidget(self.text_area)


    def set_data(self, atom_list):
        if not atom_list is None:
            self.atom_list = atom_list

    def show_data(self):

        text = ""

        for index in range(0, self.atom_list.atoms_count()):
            atom = self.atom_list.get_atom(index)

            text += "{}\t{}\t{}\t{}\n".format(str(atom.z_element),
                                              str(atom.coordinates.x),
                                              str(atom.coordinates.y),
                                              str(atom.coordinates.z) )
        self.text_area.setText(text)

    def textArea(self, height=None, width=None, readOnly=True):
        area = QTextEdit()
        area.setReadOnly(readOnly)
        area.setStyleSheet("background-color: white;")

        if not height is None: area.setFixedHeight(height)
        if not width is None: area.setFixedWidth(width)

        return area