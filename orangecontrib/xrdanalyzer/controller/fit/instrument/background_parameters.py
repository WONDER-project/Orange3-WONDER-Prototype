import numpy
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import PM2KParametersList, FitParametersList, FitParameter, Boundary

class ChebyshevBackground(FitParametersList, PM2KParametersList):
    a0 = None
    a1 = None
    a2 = None
    a3 = None
    a4 = None
    a5 = None

    def __init__(self, a0, a1, a2, a3, a4, a5):
        super(ChebyshevBackground, self).__init__()

        self.a0 = a0
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.a5 = a5

        super().add_parameter(self.a0)
        super().add_parameter(self.a1)
        super().add_parameter(self.a2)
        super().add_parameter(self.a3)
        super().add_parameter(self.a4)
        super().add_parameter(self.a5)

    def to_PM2K(self):
        text = ""

        text += self.a0.to_PM2K() + "\n"
        text += self.a1.to_PM2K() + "\n"
        text += self.a2.to_PM2K() + "\n"
        text += self.a3.to_PM2K() + "\n"
        text += self.a4.to_PM2K() + "\n"
        text += self.a5.to_PM2K() + "\n\n"

        text += "add(Chebyshev(" + \
                self.a0.parameter_name + ", " + \
                self.a1.parameter_name + ", " + \
                self.a2.parameter_name + ", " + \
                self.a3.parameter_name + ", " + \
                self.a4.parameter_name + ", " + \
                self.a5.parameter_name + "))"

        return text

    def duplicate(self):
        return ChebyshevBackground(a0=None if self.a0 is None else self.a0.duplicate(),
                                   a1=None if self.a1 is None else self.a1.duplicate(),
                                   a2=None if self.a2 is None else self.a2.duplicate(),
                                   a3=None if self.a3 is None else self.a3.duplicate(),
                                   a4=None if self.a4 is None else self.a4.duplicate(),
                                   a5=None if self.a5 is None else self.a5.duplicate())
