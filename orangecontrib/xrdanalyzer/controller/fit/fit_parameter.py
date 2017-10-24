import numpy
import orangecontrib.xrdanalyzer.util.congruence as congruence


class PM2KParametersList:

    def to_PM2K(self):
        return NotImplementedError()

class PM2KParameter:

    GLOBAL_PARAMETER = 0
    FUNCTION_PARAMETER = 1

    parameter_name = ""

    def __init__(self, parameter_name):
        self.parameter_name = parameter_name

    def to_PM2K(self, type):
        return NotImplementedError()

    def get_parameter_name(self, fixed=False):
        if self.parameter_name is None or self.parameter_name.strip() == "":
            if fixed:
                return ""
            else:
                return "@"
        else:
            return self.parameter_name

    @classmethod
    def get_type_name(cls, type):
        if type == cls.GLOBAL_PARAMETER:
            return "par"
        else:
            return ""


class Boundary:
    def __init__(self, min_value = -numpy.inf, max_value = numpy.inf):
        congruence.checkGreaterOrEqualThan(max_value, min_value, "Max Value", "Min Value")

        self.min_value = min_value
        self.max_value = max_value


class FitParameter(PM2KParameter):
    value = 0.0
    boundary = None
    fixed = False

    def __init__(self, parameter_name="", value = 0.0, boundary = Boundary(), fixed=False):
        super().__init__(parameter_name=parameter_name)
        self.value = value
        self.fixed = fixed

        if self.fixed:
            self.boundary = Boundary(min_value=self.value, max_value=self.value + 1e-12) # just a trick, to be done in a better way
        else:
            self.boundary = boundary

    def to_PM2K(self, type=PM2KParameter.GLOBAL_PARAMETER):
        text = ""

        if self.fixed:
            text += self.get_type_name(type) + " !" + self.get_parameter_name(fixed=True) + " " + str(self.value)
        else:
            text += self.get_type_name(type) + " " + self.get_parameter_name(fixed=False) + " " + str(self.value)
            
            if not self.boundary is None:
                if not self.boundary.min_value == -numpy.inf:
                    text += " min " + str(self.boundary.min_value)
                
                if not self.boundary.max_value == numpy.inf:
                    text += " max " + str(self.boundary.max_value)
        
        return text

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

    def append_to_scipy_tuple(self, parameters, boundaries):
        my_parameters, my_boundaries = self.to_scipy_tuple()

        parameters.append(my_parameters)
        boundaries.append(my_parameters)