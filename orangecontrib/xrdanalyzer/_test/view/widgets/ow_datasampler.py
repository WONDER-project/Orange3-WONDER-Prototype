import sys
import numpy

import Orange.data
from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from Orange.widgets.widget import Input,  Output, settings
from Orange.widgets.gui import separator, spin, checkBox
from orangecontrib.xrdanalyzer.util.gui.gui_utility import gui


class OWDataSamplerA(OWGenericWidget):
    name = "Data Sampler"
    description = "Randomly selects a subset of instances from data set"
    icon = "icons/datasampler.png"

    priority = 10

    class Inputs:
        data = Input("Data", Orange.data.Table)
    class Outputs:
        sample = Output("Sample Data", Orange.data.Table)
    proportion = settings.Setting(50)
    commitOnChange = settings.Setting(0)

    def __init__(self):
        super().__init__(show_automatic_box=False)

        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, "No data on input yet, waiting to "
                                          "get something")
        self.infob = gui.widgetLabel(box, '')

        separator(self.controlArea)
        self.optionBox = gui.widgetBox(self.controlArea, "Options")
        spin(self.optionBox, self, 'proportion', minv =10, maxv =90, step =10,
             label = 'Sample Size [%]:', callback =[self.selection, self.checkCommit])
        checkBox(self.optionBox, self, 'commitOnChange', 'Commit data on selection chnge')
        gui.button(self.optionBox, self, "Commit", callback = self.commit)
        self.optionBox.setDisabled(True)

    @Inputs.data
    def set_data(self,dataset):
        if dataset is not None:
            self.dataset = dataset
            self.infoa.setText('%d instances in input data set' % len(dataset))
            self.optionBox.setDisabled(False)
            self.selection()
        else:
            self.dataset = None
            self.sample = None
            self.optionBox.setDisabled(False)
            self.infoa.setText('No data on input yet, waiting to get something')
            self.infob.setText('')
        self.commit()

    def selection(self):
        if self.dataset is None:
            return
        n_selected = int(numpy.ceil(len(self.dataset)*self.proportion / 100.))
        indices = numpy.random.permutation(len(self.dataset))
        indices = indices[: n_selected]
        self.sample = self.dataset[indices]
        self.infob.setText('%d sampled instances' % len(self.sample))

    def commit(self):
        self.Outputs.sample.send(self.sample)
    def checkCommit(self):
        if self.commitOnChange:
            self.commit()