import numpy
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import PM2KParametersList, FitParametersList, FitParameter, Boundary

class Caglioti(FitParametersList, PM2KParametersList):
    U = None
    V = None
    W = None
    a = None
    b = None
    c = None

    def __init__(self, U, V, W, a, b, c):
        super(Caglioti, self).__init__()

        self.U = U
        self.V = V
        self.W = W
        self.a = a
        self.b = b
        self.c = c

        super().add_parameter(self.U)
        super().add_parameter(self.V)
        super().add_parameter(self.W)
        super().add_parameter(self.a)
        super().add_parameter(self.b)
        super().add_parameter(self.c)

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

    def duplicate(self):
        return Caglioti(U=None if self.U is None else self.U.duplicate(),
                        V=None if self.V is None else self.V.duplicate(),
                        W=None if self.W is None else self.W.duplicate(),
                        a=None if self.a is None else self.a.duplicate(),
                        b=None if self.b is None else self.b.duplicate(),
                        c=None if self.c is None else self.c.duplicate())

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