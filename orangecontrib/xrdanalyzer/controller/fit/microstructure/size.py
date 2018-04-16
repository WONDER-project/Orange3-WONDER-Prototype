
import numpy
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList


class Shape:
    NONE = "none"
    SPHERE = "sphere"
    CUBE = "cube"
    TETRAHEDRON = "tetrahedron"
    OCTAHEDRON = "octahedron"
    CYLINDER = "cylinder"

    @classmethod
    def tuple(cls):
        return [cls.NONE, cls.SPHERE, cls.CUBE, cls.TETRAHEDRON, cls.OCTAHEDRON, cls.CYLINDER]


class Distribution:
    DELTA = "delta"
    LOGNORMAL = "lognormal"
    GAMMA = "gamma"
    YORK = "york"

    @classmethod
    def tuple(cls):
        return [cls.DELTA, cls.LOGNORMAL, cls.GAMMA, cls.YORK]


class SizeParameters(FitParametersList):

    shape = Shape.SPHERE
    distribution = Distribution.LOGNORMAL
    mu = None
    sigma = None

    @classmethod
    def get_parameters_prefix(cls):
        return "size."

    def __init__(self, shape, distribution, mu, sigma):
        super(SizeParameters, self).__init__()

        self.shape = shape
        self.distribution = distribution
        self.mu = mu
        self.sigma = sigma

        super().add_parameter(self.mu)
        super().add_parameter(self.sigma)

    def to_text(self):
        text = "SIZE\n"
        text += "-----------------------------------\n"

        text += "Shape: " + self.shape + "\n"
        text += "Distribution: " + self.distribution + "\n"

        text += self.mu.to_text() + "\n"
        text += self.sigma.to_text() + "\n"

        text += "-----------------------------------\n"

        return text


    def duplicate(self):
        return SizeParameters(shape=self.shape,
                              distribution=self.distribution,
                              mu=None if self.mu is None else self.mu.duplicate(),
                              sigma=None if self.sigma is None else self.sigma.duplicate())