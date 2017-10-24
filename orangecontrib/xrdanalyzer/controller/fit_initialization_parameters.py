
class FitInitializationParameters:

    diffraction_pattern = None
    crystal_structure = None
    fft_parameters = None

    def __init__(self, diffraction_pattern = None, crystal_structure = None,
                 fft_parameters = None):
        self.diffraction_pattern = diffraction_pattern
        self.crystal_structure = crystal_structure
        self.fft_parameters = fft_parameters