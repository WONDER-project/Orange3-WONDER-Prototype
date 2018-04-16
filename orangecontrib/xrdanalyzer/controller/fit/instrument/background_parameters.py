import numpy
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList, FitParameter, Boundary

class ChebyshevBackground(FitParametersList):
    c0 = None
    c1 = None
    c2 = None
    c3 = None
    c4 = None
    c5 = None

    def get_parameters_prefix(cls):
        return "chebyshev."

    def __init__(self, c0, c1, c2, c3, c4, c5):
        super(ChebyshevBackground, self).__init__()

        self.c0 = c0
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.c4 = c4
        self.c5 = c5

        super().add_parameter(self.c0)
        super().add_parameter(self.c1)
        super().add_parameter(self.c2)
        super().add_parameter(self.c3)
        super().add_parameter(self.c4)
        super().add_parameter(self.c5)

    def to_text(self):
        text = "BACKGROUND PARAMETERS\n"
        text += "-----------------------------------\n"

        text += self.c0.to_text() + "\n"
        text += self.c1.to_text() + "\n"
        text += self.c2.to_text() + "\n"
        text += self.c3.to_text() + "\n"
        text += self.c4.to_text() + "\n"
        text += self.c5.to_text() + "\n"

        text += "-----------------------------------\n"
        
        return text       

    def duplicate(self):
        return ChebyshevBackground(c0=None if self.c0 is None else self.c0.duplicate(),
                                   c1=None if self.c1 is None else self.c1.duplicate(),
                                   c2=None if self.c2 is None else self.c2.duplicate(),
                                   c3=None if self.c3 is None else self.c3.duplicate(),
                                   c4=None if self.c4 is None else self.c4.duplicate(),
                                   c5=None if self.c5 is None else self.c5.duplicate())
