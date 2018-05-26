from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList

class FitInitialization(FitParametersList):

    diffraction_patterns = None
    crystal_structure = None
    fft_parameters = None
    thermal_polarization_parameters = None

    def __init__(self,
                 diffraction_patterns = None,
                 crystal_structure = None,
                 fft_parameters = None,
                 thermal_polarization_parameters = None):
        self.diffraction_patterns = diffraction_patterns
        self.crystal_structure = crystal_structure
        self.fft_parameters = fft_parameters
        self.thermal_polarization_parameters = thermal_polarization_parameters

    def add_diffraction_pattern(self, diffraction_pattern):
        if self.diffraction_patterns is None:
            self.diffraction_patterns = [diffraction_pattern]
        else:
            self.diffraction_patterns.append(diffraction_pattern)

    def get_diffraction_patterns(self):
        return self.diffraction_patterns

    def get_diffraction_patterns_number(self):
        return 0 if self.diffraction_patterns is None else len(self.diffraction_patterns)

    def get_diffraction_pattern(self, index):
        return self.diffraction_patterns[index]

    def set_diffraction_pattern(self, index, diffraction_pattern):
        self.diffraction_patterns[index] = diffraction_pattern

    def insert_diffraction_pattern(self, index, diffraction_pattern):
        self.diffraction_patterns.insert(index, diffraction_pattern)

    def get_parameters(self):
        parameters = []

        if not self.diffraction_pattern is None:
            for diffraction_pattern in self.diffraction_patterns:
                parameters.extend(diffraction_pattern.get_parameters())

        if not self.crystal_structure is None:
            parameters.extend(self.crystal_structure.get_parameters())

        if not self.thermal_polarization_parameters is None:
            parameters.extend(self.thermal_polarization_parameters.get_parameters())

        return parameters

    def tuple(self):
        tuple = []

        if not self.diffraction_patterns is None:
            for diffraction_pattern in self.diffraction_patterns:
                tuple.extend(diffraction_pattern.tuple())

        if not self.crystal_structure is None:
            tuple.extend(self.crystal_structure.tuple())

        if not self.thermal_polarization_parameters is None:
            tuple.extend(self.thermal_polarization_parameters.tuple())

        return tuple

    def append_to_tuple(self, parameters, boundaries):

        if not self.diffraction_patterns is None:
            for diffraction_pattern in self.diffraction_patterns:
                parameters, boundaries = diffraction_pattern.append_to_tuple(parameters, boundaries)

        if not self.crystal_structure is None:
            parameters, boundaries = self.crystal_structure.append_to_tuple(parameters, boundaries)

        if not self.thermal_polarization_parameters is None:
            parameters, boundaries = self.thermal_polarization_parameters.append_to_tuple(parameters, boundaries)

        return parameters, boundaries

    def to_text(self):
        text = "FIT INITIALIZATION\n\n"
        text += "***********************************\n\n"

        if not self.diffraction_pattern is None:
            for diffraction_pattern in self.diffraction_patterns:
                text += diffraction_pattern.to_text()

        if not self.fft_parameters is None:
            text += self.fft_parameters.to_text()

        if not self.crystal_structure is None:
            text += self.crystal_structure.to_text()

        if not self.thermal_polarization_parameters is None:
            text += self.thermal_polarization_parameters.to_text()


        text += "\n***********************************\n"

        return text


    def duplicate(self):
        if self.diffraction_patterns is None: diffraction_patterns = None
        else:
            diffraction_patterns = []
            for diffraction_pattern in self.diffraction_patterns:
                diffraction_patterns.append(diffraction_pattern.duplicate())

        return FitInitialization(diffraction_patterns=diffraction_patterns,
                                 crystal_structure=None if self.crystal_structure is None else self.crystal_structure.duplicate(),
                                 fft_parameters=None if self.fft_parameters is None else self.fft_parameters.duplicate(),
                                 thermal_polarization_parameters=None if self.thermal_polarization_parameters is None else self.thermal_polarization_parameters.duplicate())
    
