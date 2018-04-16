import numpy
import orangecontrib.xrdanalyzer.util.congruence as congruence


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

class FitParameter:
    value = 0.0
    boundary = None
    fixed = False
    function = False
    function_value = ""
    step = PARAM_ERR

    def __init__(self,
                 value=None,
                 parameter_name=None,
                 boundary=None,
                 fixed=False,
                 function = False,
                 function_value = "",
                 step=PARAM_ERR):
        self.parameter_name = parameter_name
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

    def to_parameter_text(self):
        return self.parameter_name + " = " + str(self.value)


    def to_python_code(self):
        if not self.function:
            raise ValueError("Fit parameter " + self.parameter_name + "is not a function")

        return self.parameter_name + " = " + self.function_value

    def duplicate(self):
        return FitParameter(parameter_name=self.parameter_name,
                            value=self.value,
                            fixed=self.fixed,
                            function=self.function,
                            function_value=self.function_value,
                            boundary=None if self.boundary is None else Boundary(min_value=self.boundary.min_value,
                                                                                 max_value=self.boundary.max_value))

    def is_variable(self):
        return not self.fixed and not self.function

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

    def tuple(self):
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

    def append_to_tuple(self, parameters, boundaries):
        self._check_list()
        my_parameters, my_boundaries = self.tuple()

        parameters    = list(numpy.append(parameters, my_parameters))
        boundaries[0] = list(numpy.append(boundaries[0], my_boundaries[0]))
        boundaries[1] = list(numpy.append(boundaries[1], my_boundaries[1]))

        return parameters, boundaries

    def to_text(self):
        raise NotImplementedError()

    def has_functions(self):
        for parameter in self.fit_parameters_list:
            if parameter.function: return True

        return False

    def get_available_parameters(self):
        text = ""

        for parameter in self.fit_parameters_list:
            if not parameter.function: text += parameter.to_parameter_text() + "\n"

        return text

    @classmethod
    def get_parameters_prefix(cls):
        return ""

    def get_functions_data(self):
        parameters_dictionary = {}
        python_code = ""

        for parameter in self.fit_parameters_list:
            if parameter.function:
                parameters_dictionary[parameter.parameter_name] = numpy.nan
                python_code += parameter.to_python_code() + "\n"

        return parameters_dictionary, python_code

    def set_functions_values(self, parameters_dictionary):
        for parameter in self.fit_parameters_list:
            if parameter.function:
                parameter.value = float(parameters_dictionary[parameter.parameter_name])

class FreeInputParameters:
    def __init__(self):
        self.parameters_dictionary = {}
    
    def _check_dictionary(self):
        if not hasattr(self, "parameters_dictionary"):
            self.parameters_dictionary = {}

    def get_parameters_names(self):
        self._check_dictionary()
        return self.parameters_dictionary.keys()

    def get_parameters_count(self):
        self._check_dictionary()
        return len(self.parameters_dictionary)

    def set_parameter(self, name, value):
        self._check_dictionary()
        self.parameters_dictionary[name] = value

    def get_parameter(self, name):
        self._check_dictionary()
        return self.parameters_dictionary[name]

    def append(self,parameters_dictionary):
        if not parameters_dictionary is None:
            for name in parameters_dictionary.keys():
                self.set_parameter(name, parameters_dictionary[name])

    def to_text(self):
        text = "FREE INPUT PARAMETERS\n"
        text += "-----------------------------------\n"

        if not self.parameters_dictionary is None:
            for name in self.parameters_dictionary.keys():
                text += name + " = " + str(self.get_parameter(name)) + "\n"

        text += "-----------------------------------\n"

        return text

    def to_python_code(self):
        python_text = ""

        for name in self.parameters_dictionary.keys():
            python_text += name + " = " + str(self.get_parameter(name)) + "\n"

        return python_text


class FreeOutputParameter:
    def __init__(self, expression=None, value=None):
        self.expression = expression
        self.value = value

class FreeOutputParameters:
    def __init__(self):
        self.parameters_dictionary = {}

    def _check_dictionary(self):
        if not hasattr(self, "parameters_dictionary"):
            self.parameters_dictionary = {}

    def get_parameters_count(self):
        self._check_dictionary()
        return len(self.parameters_dictionary)

    def set_parameter(self, name, parameter=FreeOutputParameter()):
        self._check_dictionary()
        if parameter is None():
            raise ValueError("Parameter object cannot be None")

        self.parameters_dictionary[name] = parameter

    def set_parameter_expression(self, name, expression):
        self._check_dictionary()
        if self.parameters_dictionary[name] is None:
            raise ValueError("Key " + name + " not found")

        self.parameters_dictionary[name].expression = expression

    def set_parameter_value(self, name, value):
        self._check_dictionary()
        if self.parameters_dictionary[name] is None:
            raise ValueError("Key " + name + " not found")

        self.parameters_dictionary[name].value = value

    def get_parameter_expression(self, name):
        self._check_dictionary()
        if self.parameters_dictionary[name] is None:
            raise ValueError("Key " + name + " not found")

        return self.parameters_dictionary[name].expression

    def get_parameter_value(self, name):
        self._check_dictionary()
        if self.parameters_dictionary[name] is None:
            raise ValueError("Key " + name + " not found")

        return self.parameters_dictionary[name].value

    def get_parameter_formula(self, name):
        self._check_dictionary()
        if self.parameters_dictionary[name] is None:
            raise ValueError("Key " + name + " not found")

        return name + " = " + self.parameters_dictionary[name].expression

    def get_parameter_full_text(self, name):
        self._check_dictionary()
        if self.parameters_dictionary[name] is None:
            raise ValueError("Key " + name + " not found")

        return name + " = " + self.parameters_dictionary[name].expression + " = " + str(self.parameters_dictionary[name].value)

    def set_formula(self, formula):
        self._check_dictionary()
        tokens = formula.split("=")
        if len(tokens) != 2: raise ValueError("Formula format not recognized: <name> = <expression>")

        self.set_parameter(name=tokens[0].strip(),
                           parameter=FreeOutputParameter(expression=tokens[1].strip()))

    def append(self, parameters_dictionary):
        if not parameters_dictionary is None:
            for name in parameters_dictionary.keys():
                self.set_parameter(name, parameters_dictionary[name])


    def to_text(self):
        text = "FREE OUTPUT PARAMETERS\n"
        text += "-----------------------------------\n"

        if not self.parameters_dictionary is None:
            for name in self.parameters_dictionary.keys():
                text += self.get_parameter_full_text(name) + "\n"

        text += "-----------------------------------\n"

        return text
