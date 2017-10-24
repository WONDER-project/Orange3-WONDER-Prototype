import numpy
import orangecontrib.xrdanalyzer.util.congruence as congruence
from orangecontrib.xrdanalyzer.controller.fit_parameter import FitParameter, Boundary, PM2KParametersList, PM2KParameter

class Simmetry:

    NONE = "none"
    FCC = "fcc"
    BCC = "bcc"
    HCP = "hcp"
    CUBIC = "cubic"


class Reflection(PM2KParameter):

    h = 0
    k = 0
    l = 0

    intensity = None

    def __init__(self, h = 1, k = 0, l = 0, intensity = FitParameter(value=100)):
        congruence.checkStrictlyPositiveNumber(intensity.value, "Intensity")

        self.h = h
        self.k = k
        self.l = l

        self.intensity = intensity

    def to_PM2K(self):
        return "addPeak(" + str(self.h) + "," + str(self.k) + "," + str(self.l) + ","  + self.intensity.to_PM2K(type=PM2KParameter.FUNCTION_PARAMETER) + ")"


class CrystalStructure(PM2KParametersList):

    a = None
    b = None
    c = None

    alpha = None
    beta = None
    gamma = None

    simmetry = "none"

    reflections = []

    def __init__(self,
                 a=FitParameter(),
                 b=FitParameter(),
                 c=FitParameter(),
                 alpha=FitParameter(),
                 beta=FitParameter(),
                 gamma=FitParameter(),
                 simmetry=Simmetry.NONE):
        self.a = a
        self.b = b
        self.c = c
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.simmetry = simmetry
        self.reflections = []

    @classmethod
    def is_cube(cls, simmetry):
        return simmetry in (Simmetry.BCC, Simmetry.FCC, Simmetry.CUBIC)

    @classmethod
    def init_cube(cls, a=FitParameter(), simmetry=Simmetry.FCC):
        if not cls.is_cube(simmetry): raise ValueError("Simmetry doesn't belong to a cubic crystal cell")

        angle = FitParameter(value=90, fixed=True)

        return CrystalStructure(a,
                                a,
                                a,
                                angle,
                                angle,
                                angle,
                                simmetry)

    def add_reflection(self, reflection=Reflection()):
        self.reflections.append(reflection)

    def set_reflection(self, index, reflection=Reflection()):
        self.reflections[index] = reflection

    def get_reflections_count(self):
        return len(self.reflections)

    def get_reflection(self, index):
        return self.reflections[index]

    def get_reflections(self):
        return numpy.array(self.reflections)


    def to_PM2K(self):

        text = ""
        if self.is_cube(self.simmetry):
            text += "addPhase(" + self.a.to_PM2K(PM2KParameter.FUNCTION_PARAMETER) + ", " + self.a.parameter_name + ", " + self.a.parameter_name + ", 90, 90, 90, “" + self.simmetry + "”)"
        else:
            text += "addPhase(" + self.a.to_PM2K(PM2KParameter.FUNCTION_PARAMETER) + \
                    ", " + self.b.to_PM2K(PM2KParameter.FUNCTION_PARAMETER) + \
                    ", " + self.c.to_PM2K(PM2KParameter.FUNCTION_PARAMETER) + \
                    ", " + self.alpha.to_PM2K(PM2KParameter.FUNCTION_PARAMETER) + \
                    ", " + self.beta.to_PM2K(PM2KParameter.FUNCTION_PARAMETER) + \
                    ", " + self.gamma.to_PM2K(PM2KParameter.FUNCTION_PARAMETER) + ", “" + self.simmetry + "”)"

        for reflection in self.reflections:
            text += "\n" + reflection.to_PM2K()

        return text

if __name__=="__main__":
    test = CrystalStructure.init_cube(a=FitParameter(parameter_name="a0", value=0.55), simmetry=Simmetry.BCC)

    print(test.to_PM2K())

    test = CrystalStructure(a=FitParameter(value=0.55), b=FitParameter(value=0.66), c=FitParameter(value=0.77),
                            alpha=FitParameter(value=10), beta=FitParameter(value=20), gamma=FitParameter(value=30),
                            simmetry=Simmetry.NONE)

    test.add_reflection(Reflection(1, 0, 3, intensity=FitParameter(value=200, boundary=Boundary(min_value=10, max_value=100000))))
    test.add_reflection(Reflection(2, 0, 0, intensity=FitParameter(value=300, boundary=Boundary(min_value=10, max_value=100000))))
    test.add_reflection(Reflection(2, 1, 1, intensity=FitParameter(value=400)))

    print(test.to_PM2K())