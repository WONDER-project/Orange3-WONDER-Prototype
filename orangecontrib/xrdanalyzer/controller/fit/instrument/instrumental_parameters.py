import numpy
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList, FitParameter, Boundary

class Caglioti(FitParametersList):
    U = None
    V = None
    W = None
    a = None
    b = None
    c = None

    @classmethod
    def get_parameters_prefix(cls):
        return "caglioti."

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


    def to_text(self):
        text = "INSTRUMENTAL PARAMETERS\n"
        text += "-----------------------------------\n"

        text += self.U.to_text() + "\n"
        text += self.V.to_text() + "\n"
        text += self.W.to_text() + "\n"
        text += self.a.to_text() + "\n"
        text += self.b.to_text() + "\n"
        text += self.c.to_text() + "\n"

        text += "-----------------------------------\n"

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

    print(test.tuple())
    print("\n")
    print(test.to_text())