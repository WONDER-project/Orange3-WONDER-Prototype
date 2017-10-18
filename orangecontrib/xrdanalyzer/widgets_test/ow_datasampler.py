import sys
import numpy

import Orange.data
from orangecontrib.xrdanalyzer.util.widgets.ow_generic_widget import OWGenericWidget
from Orange.widgets.widget import Input,  Output
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

    def __init__(self):
        super().__init__(show_automatic_box=False)

        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, "No ata on input yet, waiting to "
                                          "get something")
        self.infob = gui.widgetLabel(box, '')

    @Inputs.data
    def set_data(self,dataset):
        if dataset is not None:
            self.infoa.setText('%d instances in input data set' % len(dataset))
            indices = numpy.random.permutation(len(dataset))
            indices = indices[:int(numpy.ceil(len(dataset)*0.1))]
            sample = dataset[indices]

            self.infob.setText('%d sampled instances' % len(sample))
            self.Outputs.sample.send(sample)
        else:
            self.infoa.setText('No data on input yet, waiting to get something')
            self.infob.setText('')
            self.Outputs.sample.send("Sampled Data")