import numpy
import orangecontrib.xrdanalyzer.util.congruence as congruence
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList, FitParameter, Boundary, PM2KParametersList, PM2KParameter

class Simmetry:
    NONE = "none"
    FCC = "fcc"
    BCC = "bcc"
    HCP = "hcp"
    CUBIC = "cubic"

    @classmethod
    def tuple(cls):
        return [cls.NONE, cls.FCC, cls.BCC, cls.HCP, cls.CUBIC]

class Reflection(PM2KParameter):

    h = 0
    k = 0
    l = 0

    d_spacing = 0.0

    intensity = None

    def __init__(self, h, k, l, intensity):
        #congruence.checkPositiveNumber(intensity.value, "Intensity")

        self.h = h
        self.k = k
        self.l = l

        self.intensity = intensity

    def to_PM2K(self):
        return "addPeak(" + str(self.h) + "," + str(self.k) + "," + str(self.l) + ","  + self.intensity.to_PM2K(type=PM2KParameter.FUNCTION_PARAMETER) + ")"

    def to_text(self):
        return str(self.h) + ", " + str(self.k) + ", " + str(self.l) + ", "  + self.intensity.to_text()

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

    simmetry = Simmetry.NONE

    reflections = []

    def __init__(self, a, b, c, alpha, beta, gamma, simmetry=Simmetry.NONE):
        super(CrystalStructure, self).__init__()

        self.a = a
        self.b = b
        self.c = c
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.simmetry = simmetry
        self.reflections = []

        super().add_parameter(self.a)
        super().add_parameter(self.b)
        super().add_parameter(self.c)
        super().add_parameter(self.alpha)
        super().add_parameter(self.beta)
        super().add_parameter(self.gamma)

    @classmethod
    def is_cube(cls, simmetry):
        return simmetry in (Simmetry.BCC, Simmetry.FCC, Simmetry.CUBIC)

    @classmethod
    def init_cube(cls, a0, simmetry=Simmetry.FCC):
        if not cls.is_cube(simmetry): raise ValueError("Simmetry doesn't belong to a cubic crystal cell")

        a = FitParameter(parameter_name="cp_a", value=a0.value, fixed=a0.fixed, boundary=a0.boundary)
        b = FitParameter(parameter_name="cp_b", value=a0.value, fixed=a0.fixed, boundary=a0.boundary)
        c = FitParameter(parameter_name="cp_c", value=a0.value, fixed=a0.fixed, boundary=a0.boundary)
        alpha = FitParameter(parameter_name="alpha", value=90, fixed=True)
        beta = FitParameter(parameter_name="beta",   value=90, fixed=True)
        gamma = FitParameter(parameter_name="gamma", value=90, fixed=True)

        return CrystalStructure(a,
                                b,
                                c,
                                alpha,
                                beta,
                                gamma,
                                simmetry)

    def add_reflection(self, reflection):
        self.reflections.append(reflection)
        super().add_parameter(reflection.intensity)

        self.update_reflection(-1)

    def set_reflection(self, index, reflection):
        self.reflections[index] = reflection
        super().set_parameter(6 + index, reflection)

        self.update_reflection(index)

    def get_reflections_count(self):
        return len(self.reflections)

    def get_reflection(self, index):
        return self.reflections[index]

    def get_reflections(self):
        return numpy.array(self.reflections)

    def update_reflection(self, index):
        reflection = self.reflections[index]
        reflection.d_spacing = self.get_d_spacing(reflection.h, reflection.k, reflection.l)

    def update_reflections(self):
        for index in range(self.get_reflections_count()): self.update_reflection(index)

    def existing_reflection(self, h, k, l):
        for reflection in self.reflections:
            if reflection.h == h and reflection.k == k and reflection.l == l:
                return reflection

        return None

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
            text += "addPhase(" + self.a.to_PM2K(PM2KParameter.FUNCTION_PARAMETER) + ", " + self.a.to_PM2K(PM2KParameter.FUNCTION_PARAMETER) + ", " + self.a.to_PM2K(PM2KParameter.FUNCTION_PARAMETER) + ", 90, 90, 90, “" + self.simmetry + "”)"
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

    def parse_reflections(self, text):
        congruence.checkEmptyString(text, "Reflections")

        lines = text.splitlines()

        reflections = []

        if len(self.fit_parameters_list) > 6:
            self.fit_parameters_list = self.fit_parameters_list[:6]

        for i in range(len(lines)):
            congruence.checkEmptyString(text, "Reflections: line " + str(i+1))

            if not lines[i].strip().startswith("#"):
                data = lines[i].strip().split(",")

                if len(data) < 4: raise ValueError("Reflections, malformed line: " + str(i+1))

                h = int(data[0].strip())
                k = int(data[1].strip())
                l = int(data[2].strip())

                intensity_data = data[3].strip().split()

                if len(intensity_data) == 2:
                    intensity_name = intensity_data[0]
                    intensity_value = float(intensity_data[1])
                else:
                    intensity_name = None
                    intensity_value = float(data[3])

                boundary = None
                fixed = False

                if len(data) > 4:
                    min_value = -numpy.inf
                    max_value = numpy.inf

                    for j in range(4, len(data)):
                        boundary_data = data[j].strip().split()

                        if boundary_data[0] == "min": min_value = float(boundary_data[1].strip())
                        elif boundary_data[0] == "max": max_value = float(boundary_data[1].strip())
                        elif boundary_data[0] == "fixed": fixed = True

                    if not fixed:
                        if min_value != -numpy.inf or max_value != numpy.inf:
                            boundary = Boundary(min_value=min_value, max_value=max_value)
                        else:
                            boundary = Boundary()

                reflection = Reflection(h, k, l, intensity=FitParameter(parameter_name=intensity_name,
                                                                        value=intensity_value,
                                                                        fixed=fixed,
                                                                        boundary=boundary))
                reflections.append(reflection)

                super().add_parameter(reflection.intensity)

        self.reflections = reflections
        self.update_reflections()


    def duplicate(self):
        crystal_structure = CrystalStructure(a=None if self.a is None else self.a.duplicate(),
                                             b=None if self.b is None else self.b.duplicate(),
                                             c=None if self.c is None else self.c.duplicate(),
                                             alpha=None if self.alpha is None else self.alpha.duplicate(),
                                             beta=None if self.beta is None else self.beta.duplicate(),
                                             gamma=None if self.gamma is None else self.gamma.duplicate(),
                                             simmetry=self.simmetry)

        for reflection in self.reflections:
            reflection_copy = Reflection(h=reflection.h, k=reflection.k, l=reflection.l, intensity=None if reflection.intensity is None else reflection.intensity.duplicate())
            reflection_copy.d_spacing = reflection.d_spacing

            crystal_structure.add_reflection(reflection_copy)

        return crystal_structure

    def to_text(self):
        text = "CRYSTAL STRUCTURE\n"
        text += "-----------------------------------\n"

        text += self.a.to_text() + "\n"
        text += self.b.to_text() + "\n"
        text += self.c.to_text() + "\n"
        text += self.alpha.to_text() + "\n"
        text += self.beta.to_text() + "\n"
        text += self.gamma.to_text() + "\n"
        text += "Simmetry: " + self.simmetry + "\n"

        text += "\nREFLECTIONS\n"
        text += "h, k, l, intensity:\n"

        for reflection in self.reflections:
            text += reflection.to_text() + "\n"

        text += "-----------------------------------\n"

        return text

if __name__=="__main__":
    test = CrystalStructure.init_cube(a0=FitParameter(value=0.55, fixed=True), simmetry=Simmetry.BCC)

    print(test.to_PM2K())

    test = CrystalStructure(a=FitParameter(value=0.55), b=FitParameter(value=0.66), c=FitParameter(value=0.77),
                            alpha=FitParameter(value=10), beta=FitParameter(value=20), gamma=FitParameter(value=30),
                            simmetry=Simmetry.NONE)

    test.add_reflection(Reflection(1, 0, 3, intensity=FitParameter(value=200, boundary=Boundary(min_value=10, max_value=100000))))
    test.add_reflection(Reflection(2, 0, 0, intensity=FitParameter(value=300, boundary=Boundary(min_value=10, max_value=100000))))
    test.add_reflection(Reflection(2, 1, 1, intensity=FitParameter(value=400)))

    print(test.to_PM2K())

    text = "1, 1, 0, I110 1000, min 10\n" + \
           "2, 0, 0, I200 2000, min 20, max 10000\n"  + \
           "2, 1, 0, I210 3000, max 30000\n"  + \
           "3, 0, 0, I300 4000\n"  + \
           "3, 1, 0, 4100\n"  + \
           "4, 4, 1, I441 5000\n"

    test.parse_reflections(text)

    print(test.to_PM2K())