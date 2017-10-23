import numpy
import orangecontrib.xrdanalyzer.util.congruence as congruence
from orangecontrib.xrdanalyzer.model.boundary import Boundary

class Simmetry:

    NONE = "none"
    FCC = "fcc"
    BCC = "bcc"
    HCP = "hcp"
    CUBIC = "cubic"


class Reflection():

    h = 0
    k = 0
    l = 0

    intensity = 0.0
    intesity_boundary = None


    def __init__(self, h = 1, k = 0, l = 0, intensity = 100):
        congruence.checkStrictlyPositiveNumber(intensity)

        self.h = h
        self.k = k
        self.l = l

        self.intensity = intensity

    def set_intensity_boundary(self, boundary = Boundary(0, 100)):
        if boundary is None: raise ValueError("Boundary is None")
        congruence.checkStrictlyPositiveNumber(boundary.get_min_value(), "Boundary Min Value")

        self.intesity_boundary = boundary

class CrystalStructure():

    a = 0.0
    b = 0.0
    c = 0.0

    alpha = 0.0
    beta = 0.0
    gamma = 0.0

    simmetry = "none"

    reflections = []

    def __init__(self, a, b, c, alpha, beta, gamma, simmetry=Simmetry.NONE):
        self.a = a
        self.b = b
        self.c = c
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.simmetry = simmetry
        self.reflections = []

    @classmethod
    def init_cube(cls, a, simmetry):
        if not simmetry in (Simmetry.BCC, Simmetry.FCC, Simmetry.CUBIC):raise ValueError("Simmetry doesn't belong to a cubic crystal cell")

        return CrystalStructure(a, a, a, 90, 90, 90, simmetry)

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