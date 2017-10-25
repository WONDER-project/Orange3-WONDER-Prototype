
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

        parameters, boundaries = self.crystal_structure.append_to_scipy_tuple(parameters, boundaries)

        return parameters, boundaries
