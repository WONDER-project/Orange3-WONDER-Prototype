from orangecontrib.xrdanalyzer.controller.fit.fit_parameter import FitParametersList

class FitInitialization(FitParametersList):

    diffraction_pattern = None
    crystal_structure = None
    fft_parameters = None
    thermal_polarization_parameters = None

    def __init__(self,
                 diffraction_pattern = None,
                 crystal_structure = None,
                 fft_parameters = None,
                 thermal_polarization_parameters = None):
        self.diffraction_pattern = diffraction_pattern
        self.crystal_structure = crystal_structure
        self.fft_parameters = fft_parameters
        self.thermal_polarization_parameters = thermal_polarization_parameters

    def get_parameters(self):
        parameters = []

        # ADESSO WL e' fissa, dovra diventare un parametro di fit
        #if not self.diffraction_pattern is None:
        #    parameters.append(self.diffraction_pattern.get_parameters())

        if not self.crystal_structure is None:
            parameters.extend(self.crystal_structure.get_parameters())

        if not self.thermal_polarization_parameters is None:
            parameters.extend(self.thermal_polarization_parameters.get_parameters())

        return parameters

    def tuple(self):
        tuple = []

        # ADESSO WL e' fissa, dovra diventare un parametro di fit
        #if not self.diffraction_pattern is None:
        #    tuple.append(self.diffraction_pattern.tuple())

        if not self.crystal_structure is None:
            tuple.extend(self.crystal_structure.tuple())

        if not self.thermal_polarization_parameters is None:
            tuple.extend(self.thermal_polarization_parameters.tuple())

        return tuple

    def append_to_tuple(self, parameters, boundaries):

        # ADESSO WL e' fissa, dovra diventare un parametro di fit
        #if not self.diffraction_pattern is None:
        #parameters, boundaries = self.diffraction_pattern.append_to_tuple(parameters, boundaries)

        if not self.crystal_structure is None:
            parameters, boundaries = self.crystal_structure.append_to_tuple(parameters, boundaries)

        if not self.thermal_polarization_parameters is None:
            parameters, boundaries = self.thermal_polarization_parameters.append_to_tuple(parameters, boundaries)

        return parameters, boundaries

    def to_text(self):
        text = "FIT INITIALIZATION\n\n"
        text += "***********************************\n\n"

        if not self.diffraction_pattern is None:
            text += self.diffraction_pattern.to_text()

        if not self.fft_parameters is None:
            text += self.fft_parameters.to_text()

        if not self.crystal_structure is None:
            text += self.crystal_structure.to_text()

        if not self.thermal_polarization_parameters is None:
            text += self.thermal_polarization_parameters.to_text()


        text += "\n***********************************\n"

        return text


    def duplicate(self):
        return FitInitialization(diffraction_pattern=None if self.diffraction_pattern is None else self.diffraction_pattern.duplicate(),
                                 crystal_structure=None if self.crystal_structure is None else self.crystal_structure.duplicate(),
                                 fft_parameters=None if self.fft_parameters is None else self.fft_parameters.duplicate(),
                                 thermal_polarization_parameters=None if self.thermal_polarization_parameters is None else self.thermal_polarization_parameters.duplicate())
    
