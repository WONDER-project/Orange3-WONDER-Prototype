
class FitInitialization:

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

    def append_to_scipy_tuple(self, parameters, boundaries):

        # ADESSO WL e fissa, dovra diventare un parametro di fit
        #parameters, boundaries = self.diffraction_pattern.append_to_scipy_tuple(parameters, boundaries)

        if not self.crystal_structure is None:
            parameters, boundaries = self.crystal_structure.append_to_scipy_tuple(parameters, boundaries)

        return parameters, boundaries

    def duplicate(self):
        return FitInitialization(diffraction_pattern=None if self.diffraction_pattern is None else self.diffraction_pattern.duplicate(),
                                 crystal_structure=None if self.crystal_structure is None else self.crystal_structure.duplicate(),
                                 fft_parameters=None if self.fft_parameters is None else self.fft_parameters.duplicate())