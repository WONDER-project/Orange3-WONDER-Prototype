import numpy
import orangecontrib.xrdanalyzer.util.congruence as congruence


class Boundary:
    def __init__(self, min_value = -numpy.inf, max_value = numpy.inf):
        congruence.checkGreaterOrEqualThan(max_value, min_value, "Max Value", "Min Value")

        self.min_value = min_value
        self.max_value = max_value


class FitParameter:
    value = 0.0
    boundary = None
    fixed = False

    def __init__(self, value = 0.0, boundary = Boundary(), fixed=False):
        self.value = value
        self.fixed = fixed

        if self.fixed:
            self.boundary = Boundary(min_value=self.value, max_value=self.value + 1e-12)
        else:
            self.boundary = boundary


class FitParametersList:
    fit_parameters_list = []

    def __init__(self):
        self.fit_parameters_list = []

    def add_parameter(self, parameter = FitParameter()):
        self.fit_parameters_list.append(parameter)

    def to_scipy_tuple(self):
        parameters = []
        boundaries_min = []
        boundaries_max = []

        for fit_parameter in self.fit_parameters_list:
            parameters.append(fit_parameter.value)
            boundaries_min.append(fit_parameter.boundary.min_value)
            boundaries_max.append(fit_parameter.boundary.max_value)

        boundaries = [boundaries_min, boundaries_max]

        return parameters, boundaries

