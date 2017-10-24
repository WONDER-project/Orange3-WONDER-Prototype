import numpy
from orangecontrib.xrdanalyzer.controller.fit_parameter import PM2KParametersList, FitParametersList, FitParameter, Boundary

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


class Caglioti(FitParametersList, PM2KParametersList):
    U = None
    V = None
    W = None
    a = None
    b = None
    c = None

    def __init__(self,
               U=FitParameter(parameter_name="U", value=1e-4),
               V=FitParameter(parameter_name="V", value=1e-4),
               W=FitParameter(parameter_name="W", value=1e-4),
               a=FitParameter(parameter_name="a", value=0.5),
               b=FitParameter(parameter_name="b", value=1e-4),
               c=FitParameter(parameter_name="c", value=0.0, fixed=True)):
        self.U = U
        self.V = V
        self.W = W
        self.a = a
        self.b = b
        self.c = c

        self.add_parameter(self.U)
        self.add_parameter(self.V)
        self.add_parameter(self.W)
        self.add_parameter(self.a)
        self.add_parameter(self.b)
        self.add_parameter(self.c)

    def to_PM2K(self):
        text = ""

        text += self.U.to_PM2K() + "\n"
        text += self.V.to_PM2K() + "\n"
        text += self.W.to_PM2K() + "\n"
        text += self.a.to_PM2K() + "\n"
        text += self.b.to_PM2K() + "\n"
        text += self.c.to_PM2K() + "\n\n"

        text += "convolveFourier(CagliotiUVWabc(" + \
                self.U.parameter_name + ", " + \
                self.V.parameter_name + ", " + \
                self.W.parameter_name + ", " + \
                self.a.parameter_name + ", " + \
                self.b.parameter_name + ", " + \
                self.c.parameter_name + "))"

        return text


if __name__=="__main__":
    test = Caglioti(U=FitParameter(parameter_name="U", value=1.0, fixed=True),
                    V=FitParameter(parameter_name="V", value=2.0, boundary=Boundary(max_value=10.0)),
                    W=FitParameter(parameter_name="W", value=3.0, boundary=Boundary(min_value=-10.0)),
                    a=FitParameter(parameter_name="a", value=4.0, fixed=True),
                    b=FitParameter(parameter_name="b", value=5.0, boundary=Boundary(min_value=-10.0, max_value=10.0)),
                    c=FitParameter(parameter_name="c", value=6.0, boundary=Boundary(min_value=-10.0, max_value=10.0)))

    print(test.to_scipy_tuple())
    print("\n")
    print(test.to_PM2K())