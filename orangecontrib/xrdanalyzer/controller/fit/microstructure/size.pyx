import numpy

from orangecontrib.xrdanalyzer import is_recovery

if not is_recovery:
    from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import Boundary, FitParameter, FitParametersList
else:
    from orangecontrib.xrdanalyzer.recovery.controller.fit.fit_parameter import Boundary, FitParameter, FitParametersList


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
    add_saxs = False

    @classmethod
    def get_parameters_prefix(cls):
        return "size_"

    def __init__(self, shape, distribution, mu, sigma, add_saxs=False):
        super(SizeParameters, self).__init__()

        self.shape = shape
        self.distribution = distribution
        self.mu = mu
        self.sigma = sigma
        self.add_saxs = add_saxs

    def to_text(self):
        text = "SIZE\n"
        text += "-----------------------------------\n"

        text += "Shape: " + self.shape + "\n"
        text += "Distribution: " + self.distribution + "\n"

        text += self.mu.to_text() + "\n"
        if not self.sigma is None: text += self.sigma.to_text() + "\n"
        text += "Add SAXS: " + str(self.add_saxs)

        text += "-----------------------------------\n"

        return text


    def duplicate(self):
        return SizeParameters(shape=self.shape,
                              distribution=self.distribution,
                              mu=None if self.mu is None else self.mu.duplicate(),
                              sigma=None if self.sigma is None else self.sigma.duplicate(),
                              add_saxs=self.add_saxs)


    def get_distribution(self, auto=True, D_max=None):
        if auto: D_max = 1000

        step = D_max/1000

        x = numpy.arange(start=step, stop=D_max + step, step=step)

        try:
            try:
                from orangecontrib.xrdanalyzer.controller.fit.wppm_functions import lognormal_distribution
            except:
                from orangecontrib.xrdanalyzer.recovery.controller.fit.wppm_functions import lognormal_distribution

            if self.distribution == Distribution.LOGNORMAL:
                y = lognormal_distribution(self.mu.value, self.sigma.value, x)
            else:
                y = numpy.zeros(len(x))

            if auto:
                D_max = x[numpy.where(y > 1e-4)][-1]
                x, y, D_max = self.get_distribution(auto=False, D_max=D_max)
        except:
            pass

        return x, y, D_max


if __name__=="__main__":
    fpl = SizeParameters(shape=Shape.SPHERE,
                         distribution=Distribution.DELTA,
                         mu=FitParameter(value=10, parameter_name="mu"),
                         sigma=None, add_saxs=True)

    print(fpl.get_parameters())
