
import numpy
from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import PM2KParameter, PM2KParametersList, FitParametersList, FitParameter, Boundary


class Shape:
    NONE = "none"
    SPHERE = "sphere"
    CUBE = "cube"
    TETRAHEDRON = "tetrahedron"
    OCTAHEDRON = "octahedron"
    CYLINDER = "cylinder"

class Distribution:
    DELTA = "delta"
    LOGNORMAL = "lognormal"
    GAMMA = "gamma"
    YORK = "york"

class SizeParameters(FitParametersList, PM2KParametersList):

    shape = Shape.SPHERE
    distribution = Distribution.LOGNORMAL
    mu = None
    sigma = None

    def __init__(self,
                 shape=Shape.SPHERE,
                 distribution=Distribution.LOGNORMAL,
                 mu=FitParameter(parameter_name="mu", value=2.0, boundary=Boundary(min_value=1e-3)),
                 sigma=FitParameter(parameter_name="sigma", value=0.5, boundary=Boundary(min_value=1e-3))):
        self.shape = shape
        self.distribution = distribution
        self.mu = mu
        self.sigma = sigma

        self.add_parameter(self.mu)
        self.add_parameter(self.sigma)

    def to_PM2K(self):
        return "convolveFourier(SizeDistribution(“" + \
               self.shape + "”, ”" + \
               self.distribution + "”, " + \
               self.mu.to_PM2K(PM2KParameter.FUNCTION_PARAMETER) + ", " + \
               self.sigma.to_PM2K(PM2KParameter.FUNCTION_PARAMETER) + "))"