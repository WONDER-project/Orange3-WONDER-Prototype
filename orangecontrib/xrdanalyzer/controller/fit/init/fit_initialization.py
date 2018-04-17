from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList

class FitInitialization(FitParametersList):

    diffraction_pattern = None
    crystal_structure = None
    fft_parameters = None

    def __init__(self,
                 diffraction_pattern = None,
                 crystal_structure = None,
                 fft_parameters = None):
        self.diffraction_pattern = diffraction_pattern
        self.crystal_structure = crystal_structure
        self.fft_parameters = fft_parameters


    def has_functions(self):
        # ADESSO WL e' fissa, dovra diventare un parametro di fit
        #if not self.diffraction_pattern is None and self.diffraction_pattern.has_functions(): return True
        if not self.crystal_structure is None and self.crystal_structure.has_functions(): return True

        return False


    def set_functions_values(self, parameters_dictionary):
        # ADESSO WL e' fissa, dovra diventare un parametro di fit
        #if not self.diffraction_pattern is None:
        #    self.diffraction_pattern.set_functions_values(parameters_dictionary)

        if not self.crystal_structure is None:
            self.crystal_structure.set_functions_values(parameters_dictionary)

    def get_parameters(self):
        parameters = []

        # ADESSO WL e' fissa, dovra diventare un parametro di fit
        #if not self.diffraction_pattern is None:
        #    parameters.append(self.diffraction_pattern.get_parameters())

        if not self.crystal_structure is None:
            parameters.extend(self.crystal_structure.get_parameters())

        return parameters

    def tuple(self):
        tuple = []

        # ADESSO WL e' fissa, dovra diventare un parametro di fit
        #if not self.diffraction_pattern is None:
        #    tuple.append(self.diffraction_pattern.tuple())

        if not self.crystal_structure is None:
            tuple.extend(self.crystal_structure.tuple())

        return tuple

    def append_to_tuple(self, parameters, boundaries):

        # ADESSO WL e' fissa, dovra diventare un parametro di fit
        #parameters, boundaries = self.diffraction_pattern.append_to_tuple(parameters, boundaries)

        if not self.crystal_structure is None:
            parameters, boundaries = self.crystal_structure.append_to_tuple(parameters, boundaries)

        return parameters, boundaries

    def duplicate(self):
        return FitInitialization(diffraction_pattern=None if self.diffraction_pattern is None else self.diffraction_pattern.duplicate(),
                                 crystal_structure=None if self.crystal_structure is None else self.crystal_structure.duplicate(),
                                 fft_parameters=None if self.fft_parameters is None else self.fft_parameters.duplicate())
    
    def to_text(self):
        text = "FIT INITIALIZATION\n\n"
        text += "***********************************\n\n"
        
        if not self.diffraction_pattern is None:
            text += self.diffraction_pattern.to_text()

        if not self.fft_parameters is None:
            text += self.fft_parameters.to_text()

        if not self.crystal_structure is None:
            text += self.crystal_structure.to_text()
            

        text += "\n***********************************\n"

        return text

    def get_available_parameters(self):
        text = ""

        if not self.diffraction_pattern is None:
            text += self.diffraction_pattern.get_available_parameters()

        if not self.fft_parameters is None:
            text += self.fft_parameters.get_available_parameters()

        if not self.crystal_structure is None:
            text += self.crystal_structure.get_available_parameters()

        return text

    def get_functions_data(self):
        parameters_dictionary = {}
        python_code = ""

        if not self.diffraction_pattern is None:
            pd, pc = self.diffraction_pattern.get_functions_data()

            parameters_dictionary.update(pd)
            python_code += pc

        if not self.fft_parameters is None:
            pd, pc = self.fft_parameters.get_functions_data()

            parameters_dictionary.update(pd)
            python_code += pc

        if not self.crystal_structure is None:
            pd, pc = self.crystal_structure.get_functions_data()

            parameters_dictionary.update(pd)
            python_code += pc

    def set_functions_values(self, parameters_dictionary):
        if not self.diffraction_pattern is None:
            self.diffraction_pattern.set_functions_values(parameters_dictionary)

        if not self.fft_parameters is None:
            self.fft_parameters.set_functions_values(parameters_dictionary)

        if not self.crystal_structure is None:
            self.crystal_structure.set_functions_values(parameters_dictionary)

