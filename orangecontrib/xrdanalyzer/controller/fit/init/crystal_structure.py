import numpy
import orangecontrib.xrdanalyzer.util.congruence as congruence
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList, FitParameter, Boundary, PM2KParametersList, PM2KParameter

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

    d_spacing = 0.0

    intensity = None

    def __init__(self, h = 1, k = 0, l = 0, intensity = FitParameter(value=100)):
        congruence.checkStrictlyPositiveNumber(intensity.value, "Intensity")

        self.h = h
        self.k = k
        self.l = l

        self.intensity = intensity

    def to_PM2K(self):
        return "addPeak(" + str(self.h) + "," + str(self.k) + "," + str(self.l) + ","  + self.intensity.to_PM2K(type=PM2KParameter.FUNCTION_PARAMETER) + ")"

    def get_theta_hkl(self, wavelength):
        return numpy.degrees(numpy.asin(2*self.d_spacing/wavelength))

    def get_q_hkl(self, wavelength):
        return 8*numpy.pi*self.d_spacing/(wavelength**2)

    def get_s_hkl(self, wavelength):
        return self.get_q_hkl(wavelength)/(2*numpy.pi)

class CrystalStructure(FitParametersList, PM2KParametersList):

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
        super(FitParametersList, self).__init()

        self.a = a
        self.b = b
        self.c = c
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.simmetry = simmetry
        self.reflections = []

        self.add_parameter(self.a)
        self.add_parameter(self.b)
        self.add_parameter(self.c)
        self.add_parameter(self.alpha)
        self.add_parameter(self.beta)
        self.add_parameter(self.gamma)

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

        self.update_reflection(-1)

    def set_reflection(self, index, reflection=Reflection()):
        self.reflections[index] = reflection

        self.update_reflection(index)

    def get_reflections_count(self):
        return len(self.reflections)

    def get_reflection(self, index):
        return self.reflections[index]

    def get_reflections(self):
        return numpy.array(self.reflections)

    def update_reflection(self, index):
        reflection[index].d_spacing = self.get_d_spacing(reflection[index].h, reflection[index].k, reflection[index].l)

    def update_reflections(self):
        for index in range(self.get_reflections_count()): self.update_reflection(index)

    def get_d_spacing(self, h, k, l):
        if self.is_cube(self.simmetry):
            return numpy.sqrt(self.a.value**2/(h**2 + k**2 + l**2))
        elif self.simmetry == Simmetry.HCP:
            return 1/numpy.sqrt((4/3)*((h**2 + h*k + k**2)/ self.a.value**2  + (l/self.c.value)**2))
        else:
            NotImplementedError("Only Cubic and Hexagonal supported: TODO!!!!!!")

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