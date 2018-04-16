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
            if fixed:
                return "!" + self.parameter_name
            else:
                return self.parameter_name

    @classmethod
    def get_type_name(cls, type):
        if type == cls.GLOBAL_PARAMETER:
            return "par "
        else:
            return ""



PARAM_FIX		= 1 << 0
PARAM_SYS		= 1 << 1
PARAM_REF		= 1 << 2
PARAM_HWMIN		= -numpy.finfo('d').max
PARAM_HWMAX		= numpy.finfo('d').max
PARAM_ERR		= numpy.finfo('d').max

class Boundary:
    def __init__(self, min_value = PARAM_HWMIN, max_value = PARAM_HWMAX):
        congruence.checkGreaterOrEqualThan(max_value, min_value, "Max Value", "Min Value")

        self.min_value = min_value
        self.max_value = max_value

class FitParameter(PM2KParameter):
    value = 0.0
    boundary = None
    fixed = False
    function = False
    function_value = ""
    step = PARAM_ERR

    def __init__(self,
                 value,
                 parameter_name=None,
                 boundary=None,
                 fixed=False,
                 function = False,
                 function_value = "",
                 step=PARAM_ERR):
        super().__init__(parameter_name=parameter_name)
        self.value = value
        self.fixed = fixed
        self.function = function
        self.function_value = function_value

        if self.function:
            if self.function_value is None: raise ValueError("Function Value cannot be None")
            if self.function_value.strip() == "": raise ValueError("Function Value cannot be an empty string")

            self.fixed = False
            self.boundary = None

        if self.fixed:
            self.boundary = Boundary(min_value=self.value, max_value=self.value + 1e-12) # just a trick, to be done in a better way
        else:
            if boundary is None: self.boundary = Boundary()
            else: self.boundary = boundary

        if step is None:
            self.step = PARAM_ERR
        else:
            self.step = step

    def set_value(self, value):
        self.value = value
        self.check_value()

    def check_value(self):
        if self.value is None: raise ValueError("Parameter Value cannot be None")
        if self.function:
            if self.function_value is None: raise ValueError("Function Value cannot be None")
            if self.function_value.strip() == "": raise ValueError("Function Value cannot be an empty string")
        else:
            if not self.fixed:
                if self.boundary is None: self.boundary = Boundary()

                if self.boundary.min_value != PARAM_HWMIN:
                    if self.value < self.boundary.min_value:
                        self.value = self.boundary.min_value + (self.boundary.min_value - self.value)/2

                if self.boundary.max_value != PARAM_HWMAX:
                    if self.value > self.boundary.max_value:
                        self.value = self.boundary.max_value - (self.value - self.boundary.max_value)/2
            else:
                if self.boundary is None: self.boundary = Boundary(min_value=self.value, max_value=self.value + 1e-12)

    def to_PM2K(self, type=PM2KParameter.GLOBAL_PARAMETER):
        text = self.get_type_name(type) + self.get_parameter_name(fixed=self.fixed) + " " + str(self.value)

        if not self.fixed and not self.boundary is None:
            if not self.boundary.min_value == -numpy.inf:
                text += " min " + str(self.boundary.min_value)

            if not self.boundary.max_value == numpy.inf:
                text += " max " + str(self.boundary.max_value)
        
        return text

    def to_text(self):
        text = self.get_parameter_name() + " " + str(self.value)

        if not self.fixed:
            if not self.boundary is None:
                if not self.boundary.min_value == -numpy.inf:
                    text += ", min " + str(self.boundary.min_value)

                if not self.boundary.max_value == numpy.inf:
                    text += ", max " + str(self.boundary.max_value)
        else:
            text += ", fixed"

        return text

    def duplicate(self):
        return FitParameter(parameter_name=self.parameter_name,
                            value=self.value,
                            fixed=self.fixed,
                            function=self.function,
                            function_value=self.function_value,
                            boundary=None if self.boundary is None else Boundary(min_value=self.boundary.min_value,
                                                                                 max_value=self.boundary.max_value))

class FitParametersList:

    def __init__(self):
        self.fit_parameters_list = []

    def _check_list(self):
        if not hasattr(self, "fit_parameters_list"):
            self.fit_parameters_list = []

    def add_parameter(self, parameter):
        self._check_list()
        self.fit_parameters_list.append(parameter)

    def set_parameter(self, index, parameter):
        self._check_list()
        self.fit_parameters_list[index] = parameter

    def get_parameters_count(self):
        self._check_list()
        return len(self.fit_parameters_list)

    def get_parameters(self):
        self._check_list()
        return self.fit_parameters_list

    def append(self, fit_parameters_list):
        if not fit_parameters_list is None:
            for parameter in fit_parameters_list:
                self.fit_parameters_list.append(parameter)

    def to_scipy_tuple(self):
        self._check_list()
        parameters = []
        boundaries_min = []
        boundaries_max = []

        for fit_parameter in self.fit_parameters_list:
            parameters.append(fit_parameter.value)

            if fit_parameter.boundary is None:
                boundaries_min.append(-numpy.inf)
                boundaries_max.append(numpy.inf)
            else:
                boundaries_min.append(fit_parameter.boundary.min_value)
                boundaries_max.append(fit_parameter.boundary.max_value)

        boundaries = [boundaries_min, boundaries_max]

        return parameters, boundaries

    def append_to_scipy_tuple(self, parameters, boundaries):
        self._check_list()
        my_parameters, my_boundaries = self.to_scipy_tuple()

        parameters    = list(numpy.append(parameters, my_parameters))
        boundaries[0] = list(numpy.append(boundaries[0], my_boundaries[0]))
        boundaries[1] = list(numpy.append(boundaries[1], my_boundaries[1]))

        return parameters, boundaries



class FreeInputParameters:
    def __init__(self):
        self.__parameters_dictionary = {}
    
    def _check_hashmap(self):
        if not hasattr(self, "__parameters_dictionary"):
            self.__parameters_dictionary = {}

    def get_parameters_count(self):
        self._check_hashmap()
        return len(self.__parameters_dictionary)

    def set_parameter(self, name, value):
        self._check_hashmap()
        self.__parameters_dictionary[name] = value

    def get_parameter(self, name):
        self._check_hashmap()
        return self.__parameters_dictionary[name]

    def append(self,parameters_dictionary):
        if not parameters_dictionary is None:
            for name in parameters_dictionary.keys():
                self.set_parameter(name, parameters_dictionary[name])
    
class FreeOutputParameters:
    def __init__(self):
        self.__parameters_dictionary = {}

    def _check_hashmap(self):
        if not hasattr(self, "__parameters_dictionary"):
            self.__parameters_dictionary = {}

    def get_parameters_count(self):
        self._check_hashmap()
        return len(self.__parameters_dictionary)

    def set_parameter(self, name, expression):
        self._check_hashmap()
        self.__parameters_dictionary[name] = expression

    def get_parameter(self, name):
        self._check_hashmap()
        return self.__parameters_dictionary[name]

    def get_formula(self, name):
        self._check_hashmap()
        return name + " = " + self.__parameters_dictionary[name]

    def set_formula(self, formula):
        self._check_hashmap()
        tokens = formula.split("=")
        if len(tokens) != 2: raise ValueError("Formula format not recognized: <name> = <expression>")

        self.set_parameter(tokens[0].strip(), tokens[1].strip())

    def append(self, parameters_dictionary):
        if not parameters_dictionary is None:
            for name in parameters_dictionary.keys():
                self.set_parameter(name, parameters_dictionary[name])

