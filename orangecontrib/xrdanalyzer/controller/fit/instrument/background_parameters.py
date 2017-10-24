import numpy
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import PM2KParametersList, FitParametersList, FitParameter, Boundary

class ChebyshevBackground(FitParametersList, PM2KParametersList):
    a0 = None
    a1 = None
    a2 = None
    a3 = None
    a4 = None
    a5 = None

    def __init__(self,
               a0=FitParameter(parameter_name="a0", value=0.0),
               a1=FitParameter(parameter_name="a1", value=0.0),
               a2=FitParameter(parameter_name="a2", value=0.0),
               a3=FitParameter(parameter_name="a3", value=0.0),
               a4=FitParameter(parameter_name="a4", value=0.0),
               a5=FitParameter(parameter_name="a5", value=0.0)):
        self.a0 = a0
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.a5 = a5

        self.add_parameter(self.a0)
        self.add_parameter(self.a1)
        self.add_parameter(self.a2)
        self.add_parameter(self.a3)
        self.add_parameter(self.a4)
        self.add_parameter(self.a5)

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
