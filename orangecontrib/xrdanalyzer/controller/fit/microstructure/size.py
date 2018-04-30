
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
        return "size_"

    def __init__(self, shape, distribution, mu, sigma):
        super(SizeParameters, self).__init__()

        self.shape = shape
        self.distribution = distribution
        self.mu = mu
        self.sigma = sigma

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


    def get_distribution(self, auto=True, D_max=None):
        if auto: D_max = 1000

        step = D_max/1000

        x = numpy.arange(start=step, stop=D_max + step, step=step)
        y = numpy.zeros(len(x))

        if self.distribution == Distribution.LOGNORMAL:
            y = numpy.exp(-0.5*((numpy.log(x) - self.mu.value)/(self.sigma.value))**2)/(x*self.sigma.value*numpy.sqrt(2*numpy.pi))

        if auto:
            D_max = x[numpy.where(y > 1e-4)][-1]
            x, y = self.get_distribution(auto=False, D_max=D_max)

        return x, y